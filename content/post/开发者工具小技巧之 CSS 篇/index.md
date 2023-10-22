---
title: "6个 CSS 调试小技巧"
date: 2023-06-25
comments: true
tags: ["CSS", "DevTools"]
description: 除了查看打印日志、网络请求之外，开发者工具还提供了很多好用的功能，巧妙地使用这些功能可以大大提高我们的开发效率。本文将介绍几个与 CSS 相关的冷门开发者工具小技巧，供大家参考。
---

前端开发的过程中离不开对浏览器开发者工具的使用，我们在日常开发的过程中用的最多的应该就是 **控制台 / Console**、**元素 / Elements** 和 **网络 / Network** 面板，用来查看打印日志、DOM 元素和网络请求的状况。但其实除了这些基本的用法之外，开发者工具还提供了很多好用的功能，巧妙地使用这些功能可以大大提高我们的开发效率。本文将介绍几个和 CSS 相关的冷门小技巧，供大家参考。

> 本文中介绍的小技巧整理翻译自 [developer tools tips](https://devtoolstips.org/) 网站。

## 找到所有应用了某个样式的元素

如果你想找到页面中所有绝对定位的元素，或者是所有使用了`Grid`布局的元素，你会怎么做呢？

一种方法是在控制台中运行几行简单的 JS 代码，遍历所有的元素并检测他们的`computedStyle`来过滤出我们需要的元素。具体如下：

1. 打开开发者工具的 **控制台 / Console** 面板。
2. 复制下面这段代码到**控制台**中，把`whatToFind`对象改成你所需要过滤的样式。在这个例子中我们找的是所有绝对定位的元素。

```js
var whatToFind = {
  property: "position",
  values: ["absolute"],
};

var walker = document.createTreeWalker(
  document.documentElement,
  NodeFilter.SHOW_ELEMENT,
  (el) => {
    const style = getComputedStyle(el)[whatToFind.property];
    return whatToFind.values.includes(style)
      ? NodeFilter.FILTER_ACCEPT
      : NodeFilter.FILTER_SKIP;
  }
);

while (walker.nextNode()) {
  console.log(walker.currentNode);
}
```

3. 按下回车键，控制台就会打印出网页中所有的绝对定位元素，如图所示：

![](https://devtoolstips.org/assets/img/find-all-elements-with-style.png)

4. 如果你想找到所有使用了 `grid` 布局的元素，把`whatToFind`改成下面这样就可以：

```js
var whatToFind = {
  property: "display",
  values: ["grid", "inline-grid"],
};
```

如果你不想每次都复制这段代码到控制台中，可以把这段代码保存到开发者工具的 **Snippet** 中。

## 高亮所有匹配某条 CSS 规则的元素

如果你想知道除了当前选中的元素之外某条 CSS 规则还被应用到了哪些元素上，只要把鼠标 hover 在那条 CSS 规则上面一定的时间就可以看到了。

![](https://devtoolstips.org/assets/img/highlight-matching-elements.gif)

## 调试 CSS 动画

现代浏览器为调试和修改 CSS transitions 和动画提供了很方便的工具。我们不仅可以利用这些工具查看和调试动画，还能在其中直接修改动画的属性。具体的使用方法如下：

打开控制台的命令菜单（`Cmd+Shift+P` 或 `Ctrl+Shift+P`），输入 "Show Animations"，按下回车键，就可以打开 Animations 工具了。

接下来，触发一个网页中的动画并在工具中录制它。Animations 工具从上到下包括了四个部分：

1. 控制 / Controls： 在这个部分，你可以清除所有当前录制的动画，或者控制当前播放动画的速度。
2. 概览 / Overview：在这里可以选择某个动画，从而在 **详情 / Details** 面板中对其进行修改。
3. 时间线 / Timeline：在这里可以开始和暂停某个动画，或者跳转到动画中特定的时间点。
4. 详情 / Details：查看和修改当前选中的动画，可以增加动画的延迟或者修改动画的持续时间。

![](https://devtoolstips.org/assets/img/inspect-css-animation.gif)

## 复制元素样式

你可以通过 **Copy styles** 功能来**一次性**获取一个元素的所有样式，不需要在 Styles 面板中查看某个元素所有的 CSS 规则，然后手动地搜集其样式。通过这个功能，你可以直接获取被应用到一个元素上的所有样式，具体方法如下：

1. 在网页中找到你想要获取样式的元素，右键点击它，然后在菜单中选择 **Inspect / 检查**。
2. 在开发者工具 **Elements / 元素** 面板中，右键点击被选中的元素。
3. 在弹出的菜单中，选择 **Copy/复制 > Copy Styles/复制样式**。
4. 把复制的文本粘贴到代码编辑器或者其他你想要的地方。

![](https://devtoolstips.org/assets/img/copy-element-styles.png)

## 通过在每个元素的四周画一个方框来调试你的 CSS 和页面结构

`* { outline: 1px solid red; }`是一个简单但很强大的调试小技巧，可以用来帮助你了解页面的结构，找到溢出的 bug 以及元素布局错误的原因。具体的方法如下：

- 打开开发者工具的 **元素 / Elements** 面板
- 点击 **样式 / Styles** 侧边栏中的 `+` 号
- 给通配符选择器 `*` 添加一条规则`* { outline: 1px solid red; }`

这时页面中所有元素的轮廓就都显示出来了！
![](https://devtoolstips.org/assets/img/outline-everything.gif)

## 找到导致某个样式的 CSS 规则

想象这样一个场景：你知道某个样式被应用于你的网页中的某个元素，例如内边距，但你找不到是哪些 CSS 代码导致的。

这在大型项目中非常常见，在这类项目中，通常会有一堆 CSS 规则被应用于你正观察的这个元素。

一种解决这个难题的方法是使用 **Computed** 面板：

1. 打开开发者工具，在 **Elements / 元素** 面板选择你感兴趣的元素。
2. 打开侧边栏中的 **Computed** 面板。
3. 在列表中搜寻你感兴趣的 CSS 属性，例如`padding-bottom`。
4. 点击属性名称左侧的箭头展开详情，查看导致这个属性值的 CSS 规则。
5. 点击最右侧的链接，跳转至对应 CSS 规则在代码中的具体位置，在 Chrome 中这会把你带到 **Sources/源代码** 面板。

![](https://devtoolstips.org/assets/img/find-rule-that-causes-style-1.png)

你也可以通过点击属性名称右侧的按钮来跳转到 **Styles/样式** 面板中该 CSS 规则对应的位置。

![](https://devtoolstips.org/assets/img/find-rule-that-causes-style-2.png)

## 原文链接：

- https://devtoolstips.org/tips/en/find-all-elements-with-style/
- https://devtoolstips.org/tips/en/highlight-matching-elements/
- https://devtoolstips.org/tips/en/inspect-css-animations/
- https://devtoolstips.org/tips/en/copy-element-styles/
- https://devtoolstips.org/tips/en/outline-everything/
- https://devtoolstips.org/tips/en/find-rule-that-causes-style/
