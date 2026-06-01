/** Export chat conversation to plain text */
export function exportToTxt(chatTitle, messages) {
  const lines = [
    `AI Assistant Pro - Chat Export`,
    `Title: ${chatTitle}`,
    `Exported: ${new Date().toLocaleString()}`,
    '─'.repeat(50),
    '',
  ];

  messages.forEach((msg) => {
    const time = new Date(msg.created_at).toLocaleString();
    const role = msg.role === 'user' ? 'You' : 'AI Assistant';
    lines.push(`[${time}] ${role}:`);
    lines.push(msg.content);
    lines.push('');
  });

  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  downloadBlob(blob, `${sanitizeFilename(chatTitle)}.txt`);
}

/** Export chat conversation to PDF */
export async function exportToPdf(chatTitle, messages) {
  const { jsPDF } = await import('jspdf');
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 15;
  const maxWidth = pageWidth - margin * 2;
  let y = 20;

  doc.setFontSize(16);
  doc.text('AI Assistant Pro - Chat Export', margin, y);
  y += 10;
  doc.setFontSize(10);
  doc.text(`Title: ${chatTitle}`, margin, y);
  y += 6;
  doc.text(`Exported: ${new Date().toLocaleString()}`, margin, y);
  y += 12;

  doc.setFontSize(9);
  messages.forEach((msg) => {
    const role = msg.role === 'user' ? 'You' : 'AI Assistant';
    const time = new Date(msg.created_at).toLocaleString();
    const header = `[${time}] ${role}:`;

    if (y > 270) {
      doc.addPage();
      y = 20;
    }

    doc.setFont(undefined, 'bold');
    doc.text(header, margin, y);
    y += 5;
    doc.setFont(undefined, 'normal');

    const lines = doc.splitTextToSize(msg.content, maxWidth);
    lines.forEach((line) => {
      if (y > 280) {
        doc.addPage();
        y = 20;
      }
      doc.text(line, margin, y);
      y += 4.5;
    });
    y += 6;
  });

  doc.save(`${sanitizeFilename(chatTitle)}.pdf`);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function sanitizeFilename(name) {
  return name.replace(/[^a-z0-9]/gi, '_').substring(0, 50) || 'chat_export';
}
