---
title: "利用 CSS 实现半透明边框和多重边框"
date: 2023-06-11
comments: true
tags: ["CSS"]
description: 这篇文章整理了半透明边框、多重边框等的实现方式，供大家参考。学习这些例子还能帮助你深入掌握CSS中与边框相关的属性，包括 `border`，`outline`，`box-shadow` 等。
---

## 背景

《CSS 揭秘》这本书的第 2 章中讲到了各类特殊边框效果的实现，包括**半透明边框、多重边框**等，这篇文章对此进行了整理，大家在平常的开发过程中如果有相应的需求可以参考。学习这些例子还能帮助你深入掌握 CSS 中与边框相关的属性，包括`border`，`outline`，`box-shadow`等。

一些更加复杂的边框效果仅靠 CSS 无法实现，我的[这篇文章]()讲解了用 SVG 实现动态渐变色边框的方法，需要的朋友也可以参考。

## 半透明边框

半透明边框的效果如下图所示：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b48bb8d43ede48f4b71c93fade517057~tplv-k3u1fbpfcp-watermark.image?)

图中的图片边框是由设计师给出的一张完整图片的边缘部分。要实现这样的一个效果，我们可以考虑嵌套两层`div`，外层`div`将图片设为背景，负责图片的展示；内层`div`设置白色的背景和半透明的边框，并负责文字的展示。写成代码大概是这个样子：

```html
<style>
  .container {
    // ...
    background-image: url("...");
  }
  .inner {
    // ...
    background-color: white;
    border: 10px solid hsla(0, 0%, 100%, 0.5);
  }
</style>
<div class="container">
  <div class="inner">Hello World</div>
</div>
```

运行之后会发现效果并不符合预期，半透明的边框并没有出现。

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b49071f282734b9395ac1dbc9651e741~tplv-k3u1fbpfcp-watermark.image?)

打开开发者工具查看一下会发现原本应该是半透明边框的位置显示了纯白色。

这是因为元素的背景默认会延伸到边框的下方，而我们的边框又是半透明的白色，背景颜色的白色透过半透明的白色展示出来的仍然是纯白色。要更好地理解这一点，我们不妨把背景颜色改为黑色试试：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9bd00a17ae4940f995f537b257494104~tplv-k3u1fbpfcp-watermark.image?)

那一圈浅灰色正是边框的半透明色叠加黑色的背景颜色的结果。

要想解决这个问题，就得想办法让背景颜色不要延伸到边框所在的位置。`background-clip`属性可以帮我们实现这个目标，该属性用于控制元素背景的渲染范围。其取值包括`border-box`,`padding-box`和`content-box`，其默认值是`border-box`。聪明的你一定不难想出这几个属性各自的作用，`padding-box`可以让背景覆盖除了边框之外的区域，`content-box`可以让背景只覆盖元素盒子的`content`部分。

（如果不知道`content`，`padding`和`border`对应的区域，请复习[盒模型的知识](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/Building_blocks/The_box_model)）

回到我们的代码中，只要加上一行`background-clip: padding-box`就可以实现一开始想要的那种效果了。此时背景的纯白色不再延伸到边框处，半透明的边框下展示的是背景图片。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/072a361ea3154d099c234688e2b58e93~tplv-k3u1fbpfcp-watermark.image?)

## 多重边框

有时候设计师会要求我们给一个元素套上多个边框，但`border`属性只支持一层边框。一种比较简单的想法是嵌套多个`div`元素，但这样并不是很优雅，对于性能也会有所影响。我们可以利用`box-shadow`和`outline`属性来更加优雅地实现多重边框效果。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/46323dad11dc45b7b9f7a80d576f47a4~tplv-k3u1fbpfcp-watermark.image?)

### 使用 box-shadow 实现

我们通常使用`box-shadow`来实现阴影效果，一个典型的`box-shadow`代码如下：

```css
background-color: yellowgreen;
box-shadow: 0 5px 15px rgba(0, 0, 0, 0.6);
```

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/03dc1e535ee14b52ac21863a4681c1a4~tplv-k3u1fbpfcp-watermark.image?)

其中前两个参数对应了阴影的 **x 轴和 y 轴的偏移量**，第三个参数是阴影的**模糊半径**，可以简单地理解为阴影的大小，最后一个参数指定了阴影的颜色。这里我们得到了一个向下偏移了 5px，扩张半径为 15px 的灰色阴影。

但其实`box-shadow`还有另外一个数值参数，也就是其**扩张半径**。可以认为`box-shadow`是由无渐变投影和有渐变阴影两部分构成的，其中无渐变部分默认的大小就是元素本身的大小。扩张半径可以使无渐变部分的大小在元素本身大小的基础上增长，模糊半径控制了渐变阴影部分的大小。

平时我们使用阴影的时候通常都只是希望得到一个渐变的效果，所以不需要声明扩张半径的值（其默认值为 0），只要阴影的渐变部分就好。但我们也可以反过来想，如果把模糊半径声明为 0，扩张半径声明为某个正值，再把偏移量都设为 0，得到的效果就会像是元素的边框。

```css
box-shadow: 0 0 0 10px #655;
```

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/334eda41cb6e4f828adc9aae92e4a1d7~tplv-k3u1fbpfcp-watermark.image?)

这里我们利用`box-shadow`模拟生成了一个 15px 的灰色边框的效果。

一个元素是可以同时拥有多个`box-shadow`的，所以我们如果想要多重边框，只要再声明更多的`box-shadow`就可以了。

```css
box-shadow: 0 0 0 10px #655, 0 0 0 15px deeppink,
  0 2px 5px 15px rgba(0, 0, 0, 0.6);
```

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6414ae5796a34fa19457ef17e948c631~tplv-k3u1fbpfcp-watermark.image?)

这里我们给元素设置了三个`box-shadow`，第一个对应内层的灰色边框，第二个对应外层的粉色边框，第三个是元素最外层的阴影。

有一点要注意的是，`box-shadow`是相互交叠的，所以外层的边框必须要写在内层边框之后，在设置宽度时要把内层边框的宽度考虑进去。例如这里我们想要一个 5px 宽的粉色边框，因为内层的灰色边框已经占据了 10px，所以其宽度应该是 10 + 5 = 15px。

`box-shadow`多重边框方案在大部分情况下都非常好用，但它有两个小问题：

- `box-shadow`并不会被计入元素的`box-sizing`中，这可能会导致元素大小计算出现问题。可以通过利用`margin`或者`padding`来模拟边框占据的空间来解决这个问题。
- `box-shadow`是处在元素之外的，所以它不会捕捉相关的指针事件，例如点击、hover 等。可以通过`inset`关键字来让`box-shadow`被放置在元素之内，这时你需要添加额外的`padding`来让边框出现在正确的位置。

### 使用 outline 实现

如果你只需要双层边框，可以直接用常规的`border`属性加上`outline`属性来实现。相比于`box-shadow`，`outline`有更加灵活的样式，例如虚线。同时，我们还可以通过`outline-offset`控制`outline`距离元素边界的距离，这个距离可以是负值。我们可以借此来实现一些有趣的效果：

```css
border-radius: 10px;
outline: white dashed 1.5px;
outline-offset: -10px;
background-color: #4e403d;
```

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7a36f1d0d8f14f6b8bc77bb4b1b77236~tplv-k3u1fbpfcp-watermark.image?)

利用`outline`来实现刚刚的例子的代码如下：

```css
background: yellowgreen;
border: 10px solid #655;
outline: 15px solid deeppink;
```

## 参考资料

[CSS 揭秘 - Lea Verou](https://book.douban.com/subject/26745943/)

（本文作者 wzkMaster）
