import './app.css';
import './fonts.css';
import { mount } from 'svelte';
import ModeMaintenance from './ModeMaintenance.svelte';

const modeMaintenance = mount(ModeMaintenance, {
  target: document.getElementById('mode-maintenance')!,
});

export default modeMaintenance;
