import * as pdfjsLib from 'pdfjs-dist';
import pdfWorker from 'pdfjs-dist/build/pdf.worker.mjs?url';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

const genereImageDepuisPDF = async (response: Response, pageNumber: number) => {
  const pdfBytes = await response.arrayBuffer();

  const pdf = await pdfjsLib.getDocument({
    data: pdfBytes,
  }).promise;

  const page = await pdf.getPage(pageNumber);

  const viewport = page.getViewport({
    scale: 2,
  });

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  if (!context) {
    throw new Error('Canvas context unavailable');
  }

  canvas.width = viewport.width;
  canvas.height = viewport.height;

  await page.render({
    canvas,
    canvasContext: context,
    viewport,
  }).promise;

  return await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Failed to generate PNG'));
        return;
      }

      resolve(blob);
    }, 'image/png');
  });
};

const pagePDFenPNG = async (pdfUrl: string, pageNumber: number): Promise<Blob> => {
  const response = await fetch(pdfUrl);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  response.headers.forEach((value, key) =>
    console.log(`REPONSE : ${key}: ${value}`)
  );

  if (!response.headers.get('Content-Type')?.includes('application/pdf')) {
    const reponse = await fetch('/images/image-generique.avif');
    return reponse.blob();
  }

  return await genereImageDepuisPDF(response, pageNumber);
};

export const adaptateurPDF = {
  pagePDFenPNG,
};
