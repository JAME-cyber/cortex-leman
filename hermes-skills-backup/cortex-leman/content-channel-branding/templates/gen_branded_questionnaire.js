/**
 * Branded Client Questionnaire Generator (docx-js)
 *
 * Produces a polished Word document with:
 *   - Client logo centered at top
 *   - Brand title + subtitle in brand colors
 *   - Intro paragraph addressing the client by name
 *   - Structured Q/R table: N° (terracotta) | Question (light bg) | Answer (white, empty)
 *   - Section headers as full-width colored rows
 *   - Brand slogan footer + contact info
 *
 * Usage:
 *   1. npm install docx
 *   2. Set LOGO_PATH, OUTPUT_PATH
 *   3. Edit the `sections` array with your questions
 *   4. Adjust brand colors (TERRACOTTA, OCRE, CACAO, etc.) to match the project palette
 *   5. node gen_branded_questionnaire.js
 *
 * Validated July 2026 — Culture en Saveur (Linda questionnaire, 29 questions, 7 sections)
 */
const fs = require('fs');
const docx = require('docx');

const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, HeightRule,
  PageOrientation, VerticalAlign
} = docx;

// ── CONFIG ───────────────────────────────────────────
const LOGO_PATH = '/path/to/logo.png';          // ← Set client logo path
const OUTPUT_PATH = '/path/to/questionnaire.docx'; // ← Set output path

// Brand colors (adjust to match the project's extracted palette)
const TERRACOTTA = 'C65D3B';   // Primary accent
const OCRE = 'E8A93C';         // Section header text on dark
const CACAO = '2B1810';        // Dark background (section headers)
const WHITE = 'FFFFFF';
const LIGHT_TERRA = 'F0D2B4';  // Question cell background
const VERT = '3A6B47';         // Footer slogan
const GRAY = '666666';         // Intro text
const GRAY_LIGHT = '999999';   // Hints, contact info

// Document config
const DOC_TITLE = 'CLIENT NAME';
const DOC_SUBTITLE = 'Questionnaire de briefing';
const INTRO_TEXT = 'Bonjour [Name] ! Merci de prendre le temps de répondre à ces questions. Écris directement dans la colonne « Réponse ».';
const FOOTER_SLOGAN = 'Brand slogan here.';
const FOOTER_CONTACT = '📞 +XX  ·  ✉️ email  ·  📸 @instagram';

// ── QUESTIONS ────────────────────────────────────────
// Edit this array: [question, hint_or_empty]
const sections = [
  {
    theme: 'A. SECTION THEME',
    questions: [
      ['Question 1 ?', ''],
      ['Question 2 ?', 'Optional hint in gray italic'],
    ]
  },
  {
    theme: 'B. ANOTHER SECTION',
    questions: [
      ['Question 3 ?', ''],
    ]
  },
];

// ── HELPERS ──────────────────────────────────────────
function numCell(num) {
  return new TableCell({
    width: { size: 500, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: TERRACOTTA },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 100, bottom: 100, left: 50, right: 50 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: String(num), bold: true, size: 24, color: WHITE, font: 'Calibri' })],
    })],
  });
}

function questionCell(text) {
  return new TableCell({
    width: { size: 5000, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: LIGHT_TERRA },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 120, bottom: 120, left: 200, right: 200 },
    children: [new Paragraph({
      spacing: { before: 40, after: 40 },
      children: [new TextRun({ text, bold: true, size: 22, color: CACAO, font: 'Calibri' })],
    })],
  });
}

function answerCell(hint) {
  const children = [];
  if (hint) {
    children.push(new Paragraph({
      spacing: { before: 40, after: 40 },
      children: [new TextRun({
        text: 'Indice : ' + hint, italics: true, size: 18, color: GRAY_LIGHT, font: 'Calibri',
      })],
    }));
  }
  children.push(new Paragraph({
    spacing: { before: 40, after: 80 },
    children: [new TextRun({ text: '', size: 22 })],
  }));
  return new TableCell({
    width: { size: 6500, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: WHITE },
    verticalAlign: VerticalAlign.TOP,
    margins: { top: 120, bottom: 120, left: 200, right: 200 },
    children,
  });
}

// ── BUILD ROWS ───────────────────────────────────────
let qNum = 0;
const allRows = [];

for (const section of sections) {
  // Section header (full-width colored row)
  allRows.push(new TableRow({
    height: { value: 500, rule: HeightRule.ATLEAST },
    children: [
      new TableCell({
        width: { size: 12000, type: WidthType.DXA },
        columnSpan: 3,
        shading: { type: ShadingType.CLEAR, color: 'auto', fill: CACAO },
        verticalAlign: VerticalAlign.CENTER,
        margins: { top: 150, bottom: 150, left: 200, right: 200 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          children: [new TextRun({
            text: section.theme, bold: true, size: 26, color: OCRE, font: 'Calibri',
          })],
        })],
      }),
    ],
  }));

  for (const [q, hint] of section.questions) {
    qNum++;
    allRows.push(new TableRow({
      height: { value: 800, rule: HeightRule.ATLEAST },
      children: [numCell(qNum), questionCell(q), answerCell(hint)],
    }));
  }
}

// ── DOCUMENT ─────────────────────────────────────────
const logoData = fs.readFileSync(LOGO_PATH);
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
        margin: { top: 720, bottom: 720, left: 720, right: 720 },
      },
    },
    children: [
      // Logo
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new ImageRun({
          data: logoData,
          transformation: { width: 120, height: 120 },
          type: 'png',
        })],
      }),
      // Title
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({
          text: DOC_TITLE, bold: true, size: 36, color: TERRACOTTA, font: 'Georgia',
        })],
      }),
      // Subtitle
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({
          text: DOC_SUBTITLE, size: 22, color: CACAO, font: 'Calibri', italics: true,
        })],
      }),
      // Intro
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 200 },
        children: [new TextRun({
          text: INTRO_TEXT, size: 20, color: GRAY, font: 'Calibri',
        })],
      }),
      // Table
      new Table({
        width: { size: 12000, type: WidthType.DXA },
        columnWidths: [500, 5000, 6500],
        borders: {
          top:    { style: BorderStyle.SINGLE, size: 2, color: TERRACOTTA },
          bottom: { style: BorderStyle.SINGLE, size: 2, color: TERRACOTTA },
          left:   { style: BorderStyle.SINGLE, size: 2, color: TERRACOTTA },
          right:  { style: BorderStyle.SINGLE, size: 2, color: TERRACOTTA },
          insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'D4A57E' },
          insideVertical:   { style: BorderStyle.SINGLE, size: 1, color: 'D4A57E' },
        },
        rows: allRows,
      }),
      // Footer slogan
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400, after: 0 },
        children: [new TextRun({
          text: FOOTER_SLOGAN, italics: true, size: 22, color: VERT, font: 'Georgia',
        })],
      }),
      // Footer contact
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 0 },
        children: [new TextRun({
          text: FOOTER_CONTACT, size: 18, color: GRAY_LIGHT, font: 'Calibri',
        })],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log(`✅ Document créé: ${OUTPUT_PATH}`);
  console.log(`   Taille: ${(buffer.length / 1024).toFixed(0)} KB`);
  console.log(`   Questions: ${qNum}`);
});

// ── GOTCHAS ──────────────────────────────────────────
// 1. ImageRun REQUIRES `type: 'png'` (or 'jpg', etc.) — omitting it silently fails
// 2. Table cells need BOTH table columnWidths AND cell width (WidthType.DXA, not PERCENTAGE)
// 3. ShadingType.CLEAR (not SOLID — SOLID renders black)
// 4. Logo transformation uses points (120 ≈ ~1 inch visual), not DXA or EMU
// 5. For verification without LibreOffice: unzip the docx and check word/media/ for the logo
//    and count <w:t> text runs in word/document.xml
