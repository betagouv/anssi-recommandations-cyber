import "./app.css";
import "./fonts.css";
import Cgu from "./Cgu.svelte";
import { mount } from "svelte";

const cgu = mount(Cgu, {
  target: document.getElementById("cgu")!,
});

export default cgu;
