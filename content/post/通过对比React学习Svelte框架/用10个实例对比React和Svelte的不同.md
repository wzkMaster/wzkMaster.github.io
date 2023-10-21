---
title: "对比 React，用10个例子快速上手 Svelte"
date: 2023-07-15
comments: true
description: 文章用十个例子比较了 React 和 Svelte 两个框架，包括属性传递、状态管理、条件渲染、异步渲染等。通过阅读这篇文章，你可以了解 Svelte 的基本用法和渲染原理。
---

Svelte 和 React、Vue 一样，都是用于开发前端界面的响应式 UI 框架，让开发者能够以组件的形式组织页面代码。前几天看到油管博主 fireship 发布了[一个视频](https://www.youtube.com/watch?v=MnpuK0MK4yo)，其中用十个例子比较了 React 和 Svelte 框架的不同，感觉挺有意思的，也非常有学习价值，所以决定把其中的内容整理下来供大家阅读参考。

Svelte 已经连续多年在 Stack Overflow 的开发者调查中成为**最受喜爱的前端 UI 框架**，虽然在国内用的不多，但在国外其受欢迎程度可以说不亚于 Vue，因此也是一门非常值得关注的技术。其原理和 Vue 以及 React 也有很大的不同，能够帮助你拓展技术视野。通过阅读这篇文章，你可以了解 Svelte 的基本用法和渲染原理。

## 0. 渲染模式

React 和 Svelte 一样都是响应式 UI 框架，但它们的渲染模式却大不相同。

React 大家应该都有所了解了，它是通过**虚拟 DOM**来对页面中需要变更的部分进行计算的，这意味着每一个 React 应用都需要内置一个 Runtime，也就是一些用来负责计算虚拟 Dom 并渲染页面的代码。这会导致代码体积变大，一个 Next.js 构建的 Hello World 应用就包含了 **70kb** 的 JavaScript 代码。

而 Svelte 采取的是完全不同的策略，它会在应用构建时对开发者写的代码进行**编译**，用编译器代替了运行时，最终的产物中不会包含任何 Svelte 库的代码，所以一个 Svelte 的 Hello World 应用只有 **3kb**。

虽然 Svelte 会将非 JS 代码编译为 JS 代码，而 React 应用的代码是纯粹的 JS 代码，但令人意外的是，Svelte 能够**更好地和原生 JavaScript 第三方库进行配合**。即便如此，React 相比之下还是拥有**更加成熟的生态系统**。

## 1. state

首先我们来对比一下两个框架中进行最简单的状态管理的方式。

在 React 中，我们需要通过 useState 来生成一个响应式的状态`count` 以及其 setter - `setCount()`函数。调用`setCount()`来更新`count`的值会触发 UI 的重新渲染。

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count is {count}</button>
    </div>
  );
}
```

在 Svelte 中，只要是用`let`关键字声明的变量就是响应式的，代码中声明了一个响应式变量`count`。这里可以看到 Svelte 组件代码和 Vue 非常类似，都是分为`script`、`style`和`template`三个部分，只是在 Svelte 中不需要把 HTML 包裹在`template`标签中。要想改变`count`，只需要像改变普通的变量一样，框架就会自动进行响应式的 UI 更新。

```html
<script>
  let count = 0;
</script>

<button on:click={() => count++}>
  count is {count}
</button>
```

## 2. props

接下来我们看看两个框架中如何接收和传递属性。

React 的函数式组件属性是以函数参数的形式接收的，通常的做法是用解构赋值的方式来获取属性的具体值。

```jsx
function ColoredBox({ color }) {
  return <p>You picked: {color}</p>;
}
```

在 Svelte 中，在声明一个变量时在其最前面加上`export`关键字，就代表这个变量是外部传入的属性。

```html
<script>
  export let color; // 声明 color 属性
<script>

You picked: {color}
```

在变量的传递上，两者的语法非常类似，都是用 HTML 属性的形式传入：

```html
<App color="{color}" />
```

Svelte 还增加了一个语法糖，让我们可以用更加简洁的形式传递属性：

```html
<App {color} />
```

React 的属性可以是一个组件，Svelte 则不能。

```jsx
<App head={<Head />} />
```

## 3. children

在 React 中，我们可以通过`props.children`来获取子组件的信息。

![2023-07-14-23-24-29.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b3eda9e1a6494bed8804d57e0af1539d~tplv-k3u1fbpfcp-watermark.image?)

在 Svelte 中，需要通过插槽`slot`来实现。

```html
<!-- Widget.svelte -->
<div>
  <slot> 如果没有子组件内容，这段内容会被默认展示。 </slot>
</div>

<!-- App.svelte -->
<Widget />
<!-- ⬆️这个组件会展示默认的内容 -->

<Widget>
  <p>这个子组件会覆盖默认内容</p>
</Widget>
```

Svelte 还支持命名插槽：

```html
<!-- Widget.svelte -->
<div>
  <slot name="header" />
  <p>header 和 footer 之间的内容</p>
  <slot name="footer" />
</div>

<!-- App.svelte -->
<Widget>
  <h1 slot="header">Hello</h1>
  <p slot="footer">Copyright (c) 2019 Svelte Industries</p>
</Widget>
```

## 4. 生命周期

在 React 的函数式组件中，我们需要通过`useEffect`来模拟生命周期，如下所示：

```jsx
useEffect(() => {
  // 组件初始化时执行，相当于 onMount
  return () => {
    // 组件卸载时执行，相当于 onDestroy
  };
}, []);
```

在 Svelte 中，只要在`script`中引入相应的生命周期函数即可：

```html
<script>
  import { onMount, onDestroy } from "svelte";

  onMount(() => {
    console.log("组件挂载");
  });

  onDestroy(() => {
    console.log("组件卸载");
  });
</script>
```

## 5. 副作用

在 React 中，我们通过`useEffect`来声明副作用。通过`useEffect`的第二个参数手动声明副作用依赖的变量。

```jsx
function Counter() {
  const [count] = useState(0);

  useEffect(() => {
    document.title = `count is ${count}`;
  }, [count]);
}
```

在 Svelte 中，可以通过以`$`符号开头的响应式表达式来声明副作用。

```html
<script>
  let count = 0;

  $: document.title = `count is ${count}`;
</script>
```

在`$:`后面的语句会**自动具有响应式功能**，当语句中的引用的变量改变时，语句就会自动运行，相当于变量改变的副作用。可以看到 Svelte 并不需要我们显式地声明副作用语句依赖的变量，这比需要手动声明依赖的 React 要方便不少。

## 6. 计算属性

计算属性指的是值依赖于`state`的变量，也就是 Vue 中的`computed`。在 React 中可以通过`useMemo`来创建计算属性。`useMemo`的第一个参数是一个函数，其返回值就是计算属性的值；第二个参数是依赖数组，依赖数组中的变量改变时，计算属性的值就会重新计算。

```js
function Counter() {
  const [count] = useState(0);

  const double = useMemo(() => count * 2, [count]);
}
```

在 Svelte 中，我们同样可以使用上一节讲到的`$`表达式来创建计算属性。

```html
<script>
  let count = 0;

  $: doubled = count * 2;
</script>
```

当`count`的值变化时，`doubled`就会被重新赋值。

## 7. 条件渲染

因为 React 使用 JSX 来描述 UI，所以我们可以用 JS 的**三元表达式**来表达条件渲染的逻辑。

```jsx
function Counter() {
  const [count] = useState(0);

  return <>{count > 1000 ? <p>Big</p> : <p>Small</p>}</>;
}
```

Svelte 则是采用类似传统模版语言的语法来表达条件渲染的逻辑。

```html
<script>
  let count = 0;
</script>

{#if count > 1000}
<p>Big</p>
{:else if count > 500}
<p>Medium</p>
{:else}
<p>Small</p>
{/if}
```

相比之下，Svelte 的语法会更啰嗦一点，但是因为有`else if`语句的存在，在表达复杂的条件渲染逻辑时会比 React 的三元表达式更清晰。

## 8. 循环

在 React 中我们可以利用`map`来遍历数组并返回一系列的组件，实现循环渲染。

```jsx
function Looper() {
  const items = [
    { id: 1, name: "foo" }
    { id: 2, name: "bar" }
    { id: 3, name: "baz" }
  ]

  return <>
    {items.map(item => <p key={item.id}>{item.name}</p>)}
  </>
}
```

在 Svelte 中可以通过`each`来进行循环渲染，其中`(item.id)`表示渲染的`key`是`item.id`。

```html
<script>
  const items = [
    { id: 1, name: "foo" }
    { id: 2, name: "bar" }
    { id: 3, name: "baz" }
  ]
</script>

{#each items as item (item.id)}
<p>{item.name}</p>
{/each}
```

## 9. 全局状态管理

在 React 中，如果我们想创建多个组件共享的状态，可以通过`Context`实现。我们可以用`createContext`创建一个`CountContext`，然后在根组件`App`中用这个`Context`的`Provider`包裹其子组件，这样在子组件`Counter`中我们就可以通过`useContext`来获取到`CountContext`中的内容了。

```jsx
// context.js
import { createContext } from "react";

export const CountContext = createContext(0);

// Counter.jsx
import { useContext } from "react";
import { CountContext } from "./context";

function Counter() {
  const count = useContext(CountContext);

  return <div>{count}</div>;
}

// App.jsx
import { CountContext } from "./context";
import { Counter } from "./Counter";

function App() {
  return (
    <>
      <CountContext.Provider>
        <Counter />
      </CountContext.Provider>
    </>
  );
}
```

在 Svelte 中，我们可以通过`writable`声明全局 store。在需要使用全局状态的组件中引入 store，通过`$`+变量名的方式读取 store，调用`store.update()`更新 store。

```js
// store.js
import { writable } from "svelte/store";

export const count = writable(0);

// App.svelte
<script>
import { countStore } from "./store"
</script>

<button onClick={() => countStore.update(c => c + 1)}>
  {$countStore}
</button>
```

个人认为 Svelte 的全局状态管理语法要更加简洁一点，不需要去写什么`Provider`，只要一个`$`符号就可以使用全局状态了。

## 10. 异步渲染

React18 中引入了异步渲染的机制。我们可以使用`use`这个新的 hook 来执行异步代码，其效果类似于`await`语句。使用了`use`的组件就是异步组件，因为要等待异步代码的执行完成，组件才能渲染。

```js
function AsyncComponent() {
  const number = use(Promise.resolve(100));

  return <p>{number}</p>;
}
```

在使用异步组件时，我们可以将其包裹在`Suspense`组件中，并传入一个`fallback`组件，在异步组件还未渲染完成时会显示`fallback`组件，可以用来添加加载态。除此之外，为了防止异步渲染过程中出现错误，还可以用`ErrorBoundary`来捕捉错误，在发生错误时展示相应的`fallback`组件，避免页面白屏崩溃。

```jsx
function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <Suspense fallback={<LoadingSpinner />}>
        <ComponentWithAsyncData />
      </Suspense>
    </ErrorBoundary>
  );
}
```

在 Svelte 中，框架提供了类似 JS 的模版语法用来满足异步渲染和错误捕捉的需要。

```html
<script>
  const promise = Promise.resolve(69);
</script>

{#await promise}
<LoadingSpinner />
{:then number}
<p>The number is {number}</p>
{:catch error}
<ErrorPage {error} />
{/await}
```

## 总结

本文从 10 个层面对比了 React 和 Svelte 框架，涵盖了其渲染模式和基本用法。相信看到这里你已经对 Svelte 有一个大致的了解了。
