---
title: "[译] 现代浏览器原理（3）- 渲染流水线"
date: 2023-08-21
comments: true
description: 在这篇文章中，我们将介绍浏览器的渲染流水线，包括 HTML 解析，样式计算、布局、绘制、分层、光栅化和页面合成的具体细节。阅读本文可以让你对页面性能优化有更深的认识。
image: chrome.webp
---

> 原文链接: <https://developer.chrome.com/blog/inside-browser-part3>
>
> 原文作者：[Mariko Kosaka](https://developer.chrome.com/authors/kosamari/)

> 本文是现代浏览器原理系列博客的第 3 篇。在这个由 4 篇文章组成的博客系列中，我们将深入了解 Chrome 浏览器，从总体的架构概览到渲染流水线的具体细节，包括页面导航、渲染、合成的具体流程。如果你想知道浏览器是如何将你的代码转化为一个能够运行的网站的，或者你想了解某些性能优化技巧背后的原理，那么本系列文章就是为你量身打造的。
>
> - [现代浏览器原理（1）- Chrome 浏览器架构概览](https://juejin.cn/post/7269070543882027043)
> - [现代浏览器原理（2）- 网页导航流程](https://juejin.cn/post/7269225865619636259)
> - [现代浏览器原理（3）- 渲染流水线](https://juejin.cn/post/7269385060611047439)
> - [现代浏览器原理（4）- 处理用户输入](https://juejin.cn/post/7269321562683408399)

## 渲染进程的内部工作流程

前面的两篇文章中，我们介绍了浏览器的[多进程架构](https://juejin.cn/post/7269070543882027043)和[导航流程](https://juejin.cn/post/7269225865619636259)。在这篇文章中，我们将介绍渲染进程内部发生的事情。

渲染进程的工作原理涉及到了 web 性能的许多方面。但由于渲染进程内部发生了很多事情，因此本篇文章只是一个总体概述。如果您想深入了解，可以查看 [Google 开发者教程的 Performance](https://developers.google.com/web/fundamentals/performance/why-performance-matters/) 部分。

## 渲染进程负责展示网页的内容

渲染进程负责处理网页内发生的一切。在渲染进程中，主线程负责处理你编写的大部分 JavaScript 代码。如果你使用了 Web Worker 或 Service Worker，这部分的 JavaScript 代码会由 worker 线程处理。合成和光栅化线程也会在渲染进程中运行，从而高效流畅地呈现页面。

渲染进程的核心工作是将 HTML、CSS 和 JavaScript 代码转化为用户可以交互的网页。

![](0.jpg)

## HTML 解析

### DOM 构建

当渲染进程收到导航提交信息并开始接收 HTML 数据时，主线程就会开始解析 HTML 代码，并将其转化为 DOM 树。

DOM 是浏览器对页面的内部表示，也是前端开发者可以通过 JavaScript 与之交互的数据结构和 API。

将 HTML 文档解析为 DOM 的具体行为是由 [HTML 标准](https://html.spec.whatwg.org/)定义的。你可能已经注意到，浏览器运行 HTML 代码从不出错。例如，缺少收尾的 `</p>` 标签就是有效的 HTML。错误的 HTML 代码如 `Hi!<b>I'm <i>Chrome</b>!</i>`（b 标签在 i 标签闭合之前闭合了）会被转化为 `Hi! <b>I'm <i>Chrome</i></b><i>!</i>`。这是因为 HTML 规范旨在优雅地处理这些错误。如果你想知道这些错误具体是如何处理的，可以阅读 HTML 规范中的 "[An introduction to error handling and strange cases in the parser](https://html.spec.whatwg.org/multipage/parsing.html#an-introduction-to-error-handling-and-strange-cases-in-the-parser)" 部分。

### 子资源加载

一个网站通常会使用大量外部资源，如图片、CSS 和 JavaScript。这些文件需要从网络或缓存中加载。主线程*可以*在解析和构建 DOM 时逐个请求找到的文件，但为了加快速度，“预加载扫描器”会在 DOM 构建的过程中同步运行。如果 HTML 文档出现了 `<img>` 或 `<link>` 等内容，预加载扫描器就会提前查看 HTML 解析器生成的 token，并向浏览器进程中的网络线程发送请求。

![](1.jpg)

### JavaScript 会阻塞 HTML 解析

当 HTML 解析器遇到 `<script>` 标签时，它会暂停对 HTML 文档的解析，然后加载、解析并执行 JavaScript 代码。为什么？因为 JavaScript 可以通过 `document.write()` 等方式改变网页的内容，从而改变整个 DOM 结构，因此 HTML 解析器必须等待 JavaScript 运行后才能继续解析 HTML 文档的。如果你对 JavaScript 执行的具体过程感到好奇，[V8 团队有相关的讲座和博文](https://mathiasbynens.be/notes/shapes-ics)可以参考阅读。

### 提示浏览器如何加载资源

前端开发者可以通过多种方式提示浏览器加载资源的方式，从而优化资源加载。如果 JavaScript 不使用 `document.write()`，可以在 `<script>` 标签中添加 `async` 或 `defer` 属性。这样，浏览器就会异步加载并运行 JavaScript 代码，而不会阻塞解析过程，合适的情况下也可以使用 JavaScript module。`<link rel="preload">` 可以告知浏览器当前导航肯定需要该资源，并希望尽快下载的方式。有关这方面的更多信息，请参阅 [这篇文章](https://developers.google.com/web/fundamentals/performance/resource-prioritization)。

## 样式计算

有了 DOM 树还不足以确定页面的样子，因为我们还可以用 CSS 为页面元素添加样式。主线程会解析 CSS 并确定每个 DOM 节点的计算样式（computed style），它根据 CSS 选择器进行计算，包含了每个元素应用何种样式的信息。你可以在开发者工具的 `computed` 部分看到这些信息。

![](2.jpg)

即使不提供任何 CSS，每个 DOM 节点也会有计算样式。例如，`<h1>` 标签的显示尺寸比 `<h2>` 标签大，而且每个元素都定义了边距。这是因为浏览器有一个默认样式表，如果你想知道 Chrome 浏览器的默认 CSS 是什么样的，请[点击此处](https://cs.chromium.org/chromium/src/third_party/blink/renderer/core/html/resources/html.css)查看源代码。

## 布局

现在，渲染进程知道 DOM 结构和每个节点的样式，但这还不足以渲染页面。想象一下，你正试图通过电话向你的朋友描述一幅画。“有一个红色的大圆和一个蓝色的小方块”这些信息并不足以让你的朋友知道这幅画到底是什么样子的。

![](3.jpg)

布局是一个计算元素几何形状的过程。主线程会遍历 DOM 和计算样式来创建布局树，其中包含元素的 x y 坐标和边界框尺寸等信息。布局树的结构与 DOM 树类似，但它只包含与页面上可见内容相关的信息。如果元素应用了 `display:none`，那么该元素就不属于布局树的一部分（但如果元素的可见性为 hidden，那么它仍在布局树中）。同样，如果存在类似 `p::before{content: "Hi!"}` 这样的伪类，那么即使 DOM 中没有该元素，布局树中也会包含它。

![](4.jpg)

确定页面布局是一项很有挑战性的任务。即使是最简单的页面布局，如从上到下的块级流布局，也要考虑字体的大小和换行的位置，因为这些都会影响段落的大小和形状，进而影响下一个段落的位置。

CSS 可以让元素浮动到一侧，遮挡溢出内容，改变书写方向。可想而知，布局阶段的任务是多么艰巨。在 Chrome 浏览器中，有一整个工程师团队都在为做好元素布局而努力。如果你想了解他们的工作细节，可以看看 [BlinkOn 会议上的这些有趣的演讲](https://www.youtube.com/watch?v=Y5Xa4H2wtVA)。

## 绘制

![](5.jpg)

有了 DOM、样式和布局还不足以渲染页面。比方说，你正试图再现一幅画。你知道元素的大小、形状和位置还不够，因为你仍然需要判断绘制它们的顺序。

例如，开发者可能会为某些元素设置`z-index`，在这种情况下，按照 HTML 中元素出现的顺序绘制将导致不正确的渲染。

![](6.jpg)

在绘制步骤中，主线程会遍历布局树以创建绘制记录（paint records）。绘制记录是对页面绘制过程的详细记录，如 "先画背景，后画文本，再画矩形"。这个过程类似于使用 JavaScript 在 `<canvas>` 元素上进行过绘制。

![](7.jpg)

## 渲染流水线的更新成本很高

![](8.jpg)

渲染流水线中最重要的一点是，每一步都要使用前一步操作的结果来创建新数据。例如，如果布局树中的某些内容发生了变化，那么就需要对影响的部分重新生成绘制顺序。

如果要对元素进行动画处理，浏览器必须在每一帧之间进行这些计算。我们的大多数显示器每秒刷新屏幕 60 次（60 帧/秒）；如果每一帧都移动元素，人眼会觉得动画很流畅。但是，如果动画错过了中间的帧，页面就会显得卡顿。

![](9.jpg)

即使你的渲染操作能跟上屏幕刷新的速度，这些计算也是在主线程上运行的，这意味着当大量 JavaScript 代码运行时，它可能会被阻塞。

![](10.jpg)

您可以使用 `requestAnimationFrame()` 将 JavaScript 操作分成小块，并安排在每一帧运行，避免阻塞渲染。有关此主题的更多信息，可以参考[优化 JavaScript 执行](https://developers.google.com/web/fundamentals/performance/rendering/optimize-javascript-execution)。您还可以[在 Web Worker 中运行 JavaScript](https://www.youtube.com/watch?v=X57mh8tKkgE)，以避免阻塞主线程。

![](11.jpg)

## 合成

![](12.jpg)

现在浏览器已经知道了页面的 DOM 结构、每个元素的样式、元素的几何形状以及绘制顺序，那么它是如何绘制页面的呢？将这些信息转化为屏幕上的像素的过程称为光栅化。

处理这种情况的一个简单方法是光栅化用户当前可见的那部分内容。如果用户滚动页面，则移动光栅化的视口，将缺失的部分继续进行光栅化。Chrome 浏览器在发布之初就是这样处理光栅化的。不过，现代浏览器使用的是一种更复杂的流程，称为**合成（Compositing）**。

### 什么是合成

![](13.jpg)

合成是将页面的各个部分分层，分别光栅化，然后在一个叫合成线程的单独线程中合成页面。如果发生滚动，由于图层已经光栅化，只需合成一个新的帧即可。动画也可以用同样的方法实现，也就是移动图层和合成新帧。

你可以在开发者工具的 [Layers 面板](https://blog.logrocket.com/eliminate-content-repaints-with-the-new-layers-panel-in-chrome-e2c306d4d752?gi=cd6271834cea)查看网页是如何划分为不同层级的。

### 分层

为了进行元素层级的划分，主线程会遍历布局树以创建层级树（在开发者工具的 Performence 面板中称为 "Update Layer Tree"）。如果希望页面的某些部分获得单独的层级，可以通过 CSS 中的 `will-change` 属性提示浏览器。

![](14.jpg)

你可能很想给每个元素都添加单独的图层，但对过多的图层进行合成可能会导致运行速度变慢，甚至比每帧光栅化页面的一小部分更慢，因此做好页面渲染性能的测量至关重要。相关的信息可以参阅[这篇文章](https://developers.google.com/web/fundamentals/performance/rendering/stick-to-compositor-only-properties-and-manage-layer-count)。

### 光栅化和合成在主线程外进行

一旦创建了层级树并确定了绘制顺序，主线程就会将这些信息提交给合成线程。然后，合成线程会对每个图层进行光栅化（rasterize）处理。一个图层可能大到覆盖整个页面，因此合成线程会将它们划分为小块，并将每个块发送给光栅化线程（raster thread）。光栅化线程对每个图层进行光栅化，并将其存储在 GPU 内存中。

![](15.jpg)

合成线程可以优先处理某些光栅化线程，这样用户视口中（或附近）的内容就可以优先光栅化。一个图层还可针对不同的分辨率设置多个栅格，以处理放大等操作。

当图块光栅化完成后，合成线程会收集图块信息（称为 draw quads，绘制四边形）以创建一个合成帧（compositor frame）。

|            |                                                                    |
| ---------- | ------------------------------------------------------------------ |
| 绘制四边形 | 包含了图块在内存中的位置，以及页面合成时在哪个位置绘制图块的信息。 |
| 合成帧     | 绘制四边形的集合，表示页面的一帧。                                 |

随后合成帧会通过 IPC 提交给浏览器进程。此时，UI 线程可添加另一个合成帧，用于浏览器用户界面的更改，或从其他渲染进程添加用于扩展的合成帧。这些合成帧会被发送到 GPU，从而在屏幕上显示出来。如果发生了滚动事件，合成线程会创建另一个合成帧发送到 GPU。

合成的好处是无需主线程参与，无需等待样式计算或 JavaScript 的执行，因此速度更快。这就是为什么[仅合成动画](https://www.html5rocks.com/en/tutorials/speed/high-performance-animations/)被认为是性能最流畅的动画。如果需要再次布局或绘制，则主线程必须参与，这会延缓渲染的速度。

## 总结

在这篇文章中，我们介绍了从 HTML 解析到页面合成的渲染流水线。读完之后，你应该更加能够理解网站性能优化的相关技巧了。

在本系列的下一篇，也是最后一篇文章中，我们将更详细地了解合成线程，并探索用户进行输入（如鼠标移动和点击）时发生的情况。
