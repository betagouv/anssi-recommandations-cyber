import { mount } from "svelte";
import "./app.css";
import "./fonts.css";
import App from "./App.svelte";

const app = mount(App, {
  target: document.getElementById("app")!,
  props: {
    urlAPI: "http://localhost:8080",
  },
});

export default app;
