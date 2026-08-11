// ── Client Brief DOCX Generator (docx-js) ──
// Generic template for branded client briefs: logo + brand palette + structured questions + pricing tables.
// Adapted from Culture en Saveur "Brief Ateliers Adultes" (Aug 2026).
//
// PREREQUISITES: npm install docx
// USAGE: node gen_client_brief.js
// OUTPUT: branded DOCX with logo, brand colors, Q&A sections, pricing table, next steps

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        WidthType, AlignmentType, BorderStyle, ShadingType, HeadingLevel,
        ImageRun, PageBreak, VerticalAlign, convertInchesToTwip } = require('docx');
const fs = require('fs');

// ── BRAND CONSTANTS (replace with client's brand_identity.md values) ──
const BRAND = {
  name: 'CLIENT NAME',
  tagline: 'TAGLINE HERE',
  slogan: 'SLOGAN HERE',
  email: 'contact@example.com',
  phone: '+41 XX XXX XX XX',
  social: '@handle',
  zone: 'Genève · Suisse romande',
  logoPath: '/path/to/logo.png',
  // Palette
  primary: 'A0392B',    // Terracotta
  secondary: 'B58761',  // Ocre
  dark: '492E21',       // Cacao
  light: 'F5E8D3',      // Crème ivoire
  accent: '7A1E1E',     // Rouge profond
  sand: 'E0C0A0',       // Beige sable
};

// ── HELPERS ──
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.before ?? 0, after: opts.after ?? 120 },
    alignment: opts.align ?? AlignmentType.LEFT,
    children: [new TextRun({
      text, font: opts.font ?? 'Poppins', size: opts.size ?? 22,
      bold: opts.bold ?? false, italics: opts.italics ?? false,
      color: opts.color ?? BRAND.dark, allCaps: opts.caps ?? false,
    })],
  });
}

function heading(text, level = HeadingLevel.HEADING_1, color = BRAND.primary) {
  return new Paragraph({
    heading: level,
    spacing: { before: 300, after: 160 },
    children: [new TextRun({
      text, font: 'Playfair Display',
      size: level === HeadingLevel.HEADING_1 ? 32 : 26, bold: true, color,
    })],
  });
}

function questionItem(num, text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    indent: { left: convertInchesToTwip(0.3) },
    children: [
      new TextRun({ text: `${num}. `, font: 'Poppins', size: 22, bold: true, color: BRAND.primary }),
      new TextRun({ text, font: 'Poppins', size: 22, color: BRAND.dark }),
    ],
  });
}

function answerLine() {
  return new Paragraph({
    spacing: { before: 40, after: 200 },
    indent: { left: convertInchesToTwip(0.3) },
    border: { bottom: { style: BorderStyle.DOTTED, size: 1, color: BRAND.secondary, space: 4 } },
    children: [new TextRun({ text: '', font: 'Poppins', size: 22 })],
  });
}

function hr() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BRAND.secondary, space: 1 } },
    children: [new TextRun({ text: '' })],
  });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width ?? 50, type: WidthType.PERCENTAGE },
    verticalAlign: VerticalAlign.CENTER,
    shading: opts.bg ? { type: ShadingType.CLEAR, fill: opts.bg } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: opts.align ?? AlignmentType.LEFT,
      children: [new TextRun({
        text, font: opts.font ?? 'Poppins', size: opts.size ?? 20,
        bold: opts.bold ?? false, color: opts.color ?? BRAND.dark,
      })],
    })],
  });
}

function headerCell(text, width) {
  return cell(text, { width, bg: BRAND.primary, color: 'FFFFFF', bold: true, align: AlignmentType.CENTER, size: 20 });
}

// ── BUILD ──
async function main() {
  const logoData = fs.readFileSync(BRAND.logoPath);
  const children = [];

  // Header: Logo + Brand name + Tagline
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 100 },
    children: [new ImageRun({ data: logoData, transformation: { width: 160, height: 160 }, type: 'png' })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: BRAND.name.toUpperCase(), font: 'Playfair Display', size: 28, bold: true, color: BRAND.primary })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: BRAND.tagline, font: 'Poppins', size: 18, color: BRAND.secondary })],
  }));
  children.push(hr());

  // Title
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: 'BRIEF TITLE', font: 'Playfair Display', size: 36, bold: true, color: BRAND.primary })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    children: [new TextRun({ text: 'Subtitle — Date range', font: 'Poppins', size: 24, color: BRAND.dark, italics: true })],
  }));

  // ── Section 1: Context summary ──
  children.push(heading('1. Contexte'));
  children.push(p('Describe the client request here...', { after: 200 }));

  // ── Section 2: Questions (categorized) ──
  children.push(heading('2. Questions à valider'));
  children.push(p('Instructions for the client...', { italics: true, after: 200 }));

  // Example category
  children.push(heading('2.1. Category Name', HeadingLevel.HEADING_2));
  const questions = [
    'Question 1?',
    'Question 2?',
  ];
  questions.forEach((q, i) => { children.push(questionItem(i+1, q)); children.push(answerLine()); });

  // Page break before pricing
  children.push(new Paragraph({ children: [new PageBreak()] }));

  // ── Section 3: Pricing ──
  // Reference: see references/swiss-digital-marketing-pricing.md for current CHF rates
  children.push(heading('3. Tarifs'));
  // Build pricing table using headerCell + cell helpers

  // ── Section 4: Next steps ──
  children.push(heading('4. Prochaines étapes'));
  const steps = ['Step 1', 'Step 2', 'Step 3'];
  steps.forEach((s, i) => {
    children.push(new Paragraph({
      spacing: { before: 80, after: 80 },
      indent: { left: convertInchesToTwip(0.3) },
      children: [
        new TextRun({ text: `☐  Étape ${i+1} : `, font: 'Poppins', size: 22, bold: true, color: BRAND.primary }),
        new TextRun({ text: s, font: 'Poppins', size: 22, color: BRAND.dark }),
      ],
    }));
  });

  // Footer
  children.push(hr());
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `${BRAND.name}  ·  ${BRAND.email}  ·  ${BRAND.phone}`, font: 'Poppins', size: 18, color: BRAND.secondary })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `${BRAND.social}  ·  ${BRAND.zone}`, font: 'Poppins', size: 18, color: BRAND.secondary })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: BRAND.slogan, font: 'Poppins', size: 16, color: BRAND.primary, bold: true })],
  }));

  const doc = new Document({
    creator: BRAND.name,
    title: 'Brief Title',
    styles: { default: { document: { run: { font: 'Poppins', size: 22, color: BRAND.dark } } } },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 }, // 2cm
        },
      },
      children,
    }],
  });

  const buf = await Packer.toBuffer(doc);
  const outPath = 'output/Brief_Client.docx';
  fs.writeFileSync(outPath, buf);
  console.log('✅ DOCX: ' + outPath + ' (' + (buf.length / 1024).toFixed(1) + ' KB)');
}

main().catch(e => { console.error(e); process.exit(1); });
