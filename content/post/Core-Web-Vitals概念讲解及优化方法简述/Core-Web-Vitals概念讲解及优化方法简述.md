---
title: "Core Web Vitals概念讲解及优化方法简述"
date: 2023-05-03
comments: true
categories:
  - 前端工程化
tags:
  - JavaScript
  - 性能优化
---

众所周知，性能优化对于前端开发来说非常重要，特别是对于ToC的Web应用来讲，如果你的网页使用起来太过卡顿，用户就会选择离开，去使用别人的网站。虽然网络的速度和计算机的性能不断在提升，但我们传输的Web应用体积也在变得越来越大和越来越复杂，更何况不是所有人都能够享受快速稳定的网络连接和高性能的计算机。所以我们必须要掌握性能优化的方法，才能保证大部分用户的体验良好，提高网站的受欢迎程度。

大部分的性能优化教程都是围绕网络、浏览器渲染来进行展开，从开发者的角度分析可以做的事情。本文采用了一种不同的视角，我们**从用户的角度**来看：什么样的网站是一个性能良好的网站？答案会是**加载迅速、交互响应快、浏览体验好**等等。那我们就可以从这些方面切入，来看有哪些可以做的性能优化尝试。当然了，作为开发者，我们仅仅知道这些定性描述是不够的，还需要可以量化的指标，才能准确地进行测量和提升。

Google 已经帮我们解决了这个问题，[Web Vitals](https://web.dev/vitals/)（网页体验指标）是由 Google 提出的一系列前端性能指标，用于衡量一个网站的性能和用户体验。其中最核心的是 Core Web Vitals，其中包括了三个指标，分别是 **LCP（Largest Contentful Paint，最大内容绘制），FID（First Input Delay，首次输入延迟），CLS（Cumulative Layout Shift，累计布局偏移）**。Google 通过一系列的用户研究提出了这些指标，并把它们用于自家搜索引擎对网站的性能评价中，所以是非常值得参考的。通过针对性地优化这些指标，我们可以更有方向地进行性能优化，从而提升网页的用户体验。

## Core Web Vitals 概念讲解

首先我们了解一下各个指标的具体含义。

### LCP（Largest Contentful Paint，最大内容绘制）

LCP 测量的是**网页中面积最大的一块内容加载完成的时间**，它代表着**用户感知页面加载（基本上）完成的时间**。

以掘金的主页为例，从骨架屏中我们可以看出最大的一块内容应该是首页的文章列表。因此LCP的时间就是页面开始加载到文章列表显示出来的时间。

![frame_chrome_mac_dark (38).png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/482e6956a3604782be5e3e0adb769b07~tplv-k3u1fbpfcp-watermark.image?)

### FID（First Input Delay，首次输入延迟）

FID 测量的是从**用户第一次与页面交互到浏览器对交互作出响应所经过的时间**。这里的交互包括了点击链接、按钮，在输入框中输入文字等。它反映出了**网站对用户交互的响应速度**。

### CLS（Cumulative Layout Shift，累计布局偏移）

CLS 测量的是**页面加载过程中各个元素偏移的距离总和**，它反映的并不是网页加载的速度和响应时间，而是**加载过程中的用户体验**。

CLS对用户体验的影响可以通过下面这个例子看出：

![cls.gif](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a5a69ed650254d05b90b7c151c6c3728~tplv-k3u1fbpfcp-watermark.image?)

图中用户想要点击返回按钮时，页面上方弹出了一段新的文字，导致用户误点为提交订单。类似的情况通常是由异步加载的图片或广告导致，如果没有进行恰当的处理，这些元素的异步加载会导致页面的重新布局，破坏用户体验。

## 测量方法

没有调查就没有发言权。想要对网页性能进行优化，我们首先得对网页的性能指标进行测量，找出性能瓶颈，对症下药。

### Lighthouse

在本地调试时，我们可以通过Chrome开发者工具中的Lighthouse面板来查看网页的Core Web Vitals情况。打开Chrome开发者工具，选择LightHouse面板。如果看不到Lighthouse这个Tab的话就点右侧的⏩，下拉框中可以找到Lighthouse。

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/05e8bafbb9654f77b315356a484b97eb~tplv-k3u1fbpfcp-watermark.image?)

注意在使用Lighthouse分析网站性能时最好是将开发者工具单独为一个窗口，不要和测试页面的窗口挤在一起，因为这样才能反映正常屏幕宽度下网站性能的情况。默认Lighthouse会对Accessibility，PWA等都进行检测，这些我们并不需要，所以取消勾选即可。最后点击右上方的蓝色按钮开始分析网页性能。

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6d34b394126643be91b72664e6f02cee~tplv-k3u1fbpfcp-watermark.image?)

以掘金的分析结果为例，我们可以看到最上面的是网页的总体分数，接下来的一栏就是网页的性能指标情况。其中出现了我们提到的LCP和CLS，而FID实际上就相当于First Contentful Paint + Total Blocking Time。报告中显示为绿色的说明该指标情况良好，如果是黄色说明有待提高，红色则表明需要多加注意。

![报告1.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/707b58f46dc745df90c7337663896ae4~tplv-k3u1fbpfcp-watermark.image?)

再往下滚动可以看到报告中还给出了一些具体的优化建议，我们可以在右上角通过相关的指标来筛选建议。

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d66edc9d9672493aaf88b3d149a3dd29~tplv-k3u1fbpfcp-watermark.image?)

点击其中的某个建议，例如“给图片添加`height`和`width`“，可以看到开发者工具已经贴心地告诉我们是哪些图片有这个问题，以及改进这一点所能够改善的Web Vitals指标。

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bc8a8ba393404bb7951ce568b8f2edf6~tplv-k3u1fbpfcp-watermark.image?)

### 代码测量

单靠本地调试的方法来测试网页性能显然是不够的，因为本地测试只能反映应用在开发者的电脑上运行的情况，而开发者的机器性能和网络状况往往比普通的用户要好。所以我们更应该关注的是用户访问网站时的指标情况，对此我们可以利用浏览器给我们提供的`PerformanceObserver`API。

对于LCP，我们可以通过如下的代码进行测量：

```js
const metrics = {
  lcp: 0,
  fid: 0,
  cls: 0,
}

new PerformanceObserver((entryList) => {
    let entries = entryList.getEntries() || [];
    entries.forEach((entry) => {
      // 比对每个阶段的LCP和当前记录的LCP，记录最大的LCP值
      if (entry.startTime > metrics.lcp) {
        payload.lcp = entry.startTime;
        console.log(`LCP: ${metrics.lcp}`);
      }
    });
}).observe({ type: "largest-contentful-paint", buffered: true });
```

我们调用`new PerformanceObserver(cb).observe(options)`函数，在`options`中告诉它我们要观察`largest-contentful-paint`，也就是LCP。`buffed: true`表示即使相应的性能指标在`PerformanceObserver`就已经记录，也会被缓存下来。

要注意的是LCP有可能会是一系列不同的值，原因是`PerformanceObserver`记录的是每个时刻网页中最大的内容完成渲染的时间，以上文提到的掘金主页为例：网页中最快渲染出来的是顶部的tab栏，我们假设它在`0.5s`完成了渲染，这时网页中面积最大的元素也是它，所以此时的LCP是`0.5s`；随后`1.2s`时两侧的侧边栏模块也渲染完成了，但此时网页中面积最大的元素还是tab栏，那么LCP就依然是`0.5s`；最后在`2s`时文章列表也渲染完成了，此时网页中最大的元素就变成了文章列表，相应地，LCP也变成了`2s`。

这就是为什么在`PerformanceObserver`的回调中我们要比对每个`entry`的`startTime`（也就是每个阶段记录的LCP）和当前记录的LCP，这样我们才能找到最大的LCP值，这个值就是真正的网页LCP。

对于FID的测量，我们使用的代码也非常类似：

```js
new PerformanceObserver((entryList) => {
    let entries = entryList.getEntries() || [];
    entries.forEach((entry) => {
      metrics.fid = entry.processingStart - entry.startTime;
      console.log(`FID: ${metrics.fid}`);
    });
}).observe({ type: "first-input", buffered: true });
```

我们没有办法直接获取到FID的值，而是观察`first-input`的情况，通过将其触发时间`entry.startTime`与真正的处理开始时间`entry.processingStart`进行相减，可以得到FID的值。

CLS的测量代码也跟上面两个指标差不多：

```js
new PerformanceObserver((entryList) => {
    let entries = entryList.getEntries() || [];
    entries.forEach((entry) => {
      if (!entry.hadRecentInput) {
        metrics.cls += entry.value;
        console.log(`CLS: ${metrics.cls}`);
      }
    });
}).observe({ type: "layout-shift", buffered: true });
```

CLS的含义是页面加载过程中各个元素偏移的距离总和，所以我们观察页面的`layout-shift`事件，将每一次布局偏移的值都累加到CLS的值中，最终就可以算出用户使用过程中的累计布局偏移量。

不难发现这种写法还是很繁琐的，所以 Google 为我们封装了`web-vitals`库，利用这个库我们可以更方便地获取Web Vitals的值。其使用示例如下所示：

```js
import {onCLS, onFID, onLCP} from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify(metric);
  // 如果`navigator.sendBeacon()`可以使用就用, 否则使用`fetch()`将性能数据发送至服务器。
  (navigator.sendBeacon && navigator.sendBeacon('/analytics', body)) ||
      fetch('/analytics', {body, method: 'POST', keepalive: true});
}

onCLS(sendToAnalytics);
onFID(sendToAnalytics);
onLCP(sendToAnalytics);
```

其中 `sendBeacon` 和普通的`fetch`请求区别在于：`sendBeacon` 适用于在页面卸载或关闭时需要发送数据的场景，例如发送统计数据或日志等。这是因为 `sendBeacon` 只能使用POST方法发送数据，且没有回调函数，但它不会阻塞页面的卸载，所以可以提高浏览器重新导航的速度。

## 优化方法

### LCP（最大内容绘制）优化

对于大部分的网站首页来说，Largest Content都是banner图之类的图片。那么我们就应该想办法让这张图片加载出来的速度更快，要做到这一点，我们有三个努力的方向：

1. **推迟不必要的资源加载**，让主要图片的请求优先进行。一个网站在初始化时需要请求的东西是非常多的，包括css文件、js文件、字体文件以及大量的图片。我们不妨看一看掘金首页加载时请求了多少东西。

    ![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f6de28f92d47423e82f70ef1f804eecf~tplv-k3u1fbpfcp-watermark.image?)
    
    由于屏幕大小的限制，我并没有把所有的请求都截到图里面，但已经不难看出请求的文件个数非常的多。而一个页面通常一次性只能并发6-8个请求，所以如果我们没有做好处理，关键图片的请求可能排队就要排很久。

    在上面提到的初始化需要的文件中，字体文件和CSS文件肯定是要优先加载的，因为它和图片一样都是渲染页面所必须的。但对于一些次要的js文件和图片文件，就可以考虑延迟其加载，来给关键图片加载让路。

    js文件的延迟加载可以通过`defer`属性来实现，当浏览器遇到带有`defer`属性的js文件时，它会将该文件的加载推迟到文档解析完成后再进行。

    图片文件可以通过在其元素中添加`loading="lazy"`属性来实现懒加载。对于添加了`loading="lazy"`属性的图片，浏览器会在其进入可视区域后再进行加载。

2. **优化图片大小**。由于决定LCP的大部分是图片，所以我们可以对主要图片的大小进行优化，有以下几种具体方法：
      
      a. 使用体积更小的图片格式，比如`webp`。

      b. 利用工具对图片进行无损压缩，例如node中的`imagemin`库。

      c. 使用响应式图片，根据屏幕的大小对请求的图片分辨率进行调整。小屏幕下并不需要看太高分辨率的图片，所以可以传输更小的低分辩率图片。对此HTML也是有原生的支持的：
      ```html
      <!-- srcset告诉浏览器在不同的宽度下对应的图片链接，sizes则是用于告诉浏览器我们对于不同宽度的定义 -->
      <img src="picture-1200.jpg"

          srcset="picture-600.jpg 600w,
          picture-900.jpg 900w,
          picture-1200.jpg 1200w"

          sizes="(max-width: 600px) 600px,
          (max-width: 900px) 900px,
          1200px" />
      ```

3. **提高关键图片的网络请求速度**。对于如何提高网络请求的速度相信大家应该都比较熟悉了，这里简单列举几种方法：
   
   a. 使用HTTP/2，其二进制传输和多路复用机制能够提高网络请求的速度。

   b. 利用CDN将用户请求的资源分发到距离用户最近的节点，避免长距离的数据传输。

   c. 利用HTTP缓存来避免不必要的重复请求。
   
   [这篇文章](https://juejin.cn/post/6892994632968306702)中对于网络请求的优化有更详细的论述，大家有需要的话可以参考。
   
### FID（首次输入延迟）优化

FID对应的其实就是相关JS文件解析完成的时间，因为只有JS解析完了页面才能对用户输入做出反应。因此优化FID也就意味着优化JS文件的加载和解析速度，说到底就是要传输尽量少的JS文件，同时提高JS文件的传输速度。

1. 要想传输更少的JS文件，我们首先可以利用打包工具的**split chunks**（代码分包）和**tree shaking**功能来删除重复和无用的代码。然后再利用 `UglifyJS` 之类的代码压缩工具对代码进行进一步的压缩。

2. 提高JS文件的传输速度其实就是提高网络请求的速度，相关的方法在上面已经列举了一些，这里就不再赘述了。

### CLS（累计布局偏移）优化

布局偏移的解决方法比较直观，就是给那些可能会延迟加载出来的元素设定**占位符/骨架屏**。如果不清楚页面中有哪些元素导致了布局偏移，也可以通过上文所说的Lighthouse进行查看，再对症下药。除了使用**骨架屏**，也可以直接通过HTML的`height`和`width`属性，来让浏览器事先了解相关元素的大小（这被称为“Layout Hints” - 布局提示），这样在布局页面的时候浏览器就会把元素的宽高计算在内，元素加载出来时就不需要重新布局了。

```html
<!-- 通过width和height告诉浏览器这是一张640*480的图片 -->
<img width="640" height="480" src="...">
```

除此之外，一些页面中的动态元素可能也会影响CLS。对于这些动态元素，可以**通过绝对定位等方式让其脱离文档流**，避免对其他元素的影响，造成浏览器大规模的重新布局。

对于**元素尺寸、位置的改变尽量通过`transform`实现**，因为`transform`不会改变元素在文档流中的位置，也就不会影响其他元素的布局。

## 总结

本文介绍了Google提出的三个核心网站性能指标（Core Web Vitals），分别是LCP、FID和CLS，介绍了其概念、测量和优化方法：

1. LCP（Largest Contentful Paint，最大内容绘制）指的是**网页中面积最大的一块内容加载完成的时间**，可以通过**推迟不必要的资源加载、优化图片和提高图片请求速度**来优化LCP。
2. FID（First Input Delay，首次输入延迟）指的是**用户第一次与页面交互到浏览器对交互作出响应所经过的时间**，通过**压缩JS文件和提高JS文件传输速度**可以优化LCP。
3. CLS（Cumulative Layout Shift，累计布局偏移）指的是**页面加载过程中各个元素偏移的距离总和**，利用骨架屏、布局提示、绝对定位以及`transform`等技术可以有效减少页面的CLS。

上述的三个指标都可以通过浏览器提供的`PerformanceObserver` API来进行测量，`web-vitals`等工具库对这个API进行了封装，更方便使用。在实际开发中我们可以利用Lighthouse来分析潜藏的性能问题，从而对症下药。

（本文作者wzkMaster）
