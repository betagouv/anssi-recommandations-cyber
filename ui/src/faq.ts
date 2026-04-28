import './app.css';
import './fonts.css';
import Faq from './Faq.svelte';
import { mount } from 'svelte';

const faq = mount(Faq, {
  target: document.getElementById('faq')!,
});

export default faq;
