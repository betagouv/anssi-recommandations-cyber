import './app.css';
import './fonts.css';
import PolitiqueConfidentialite from './PolitiqueConfidentialite.svelte';
import { mount } from 'svelte';

const politiqueDeConfidentialite = mount(PolitiqueConfidentialite, {
  target: document.getElementById('politique-confidentialite')!,
});

export default politiqueDeConfidentialite;
