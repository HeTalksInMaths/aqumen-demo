export const parseQuestion = (question) => {
  const parsedLines = [];
  const errorPositions = [];

  question.code.forEach((line, lineIndex) => {
    let cleanLine = line;
    let processedChars = 0;

    const delimiterRegex = /<<([^>]+)>>/g;
    let match;

    while ((match = delimiterRegex.exec(line)) !== null) {
      const errorText = match[1];
      const startPos = match.index - processedChars;
      const endPos = startPos + errorText.length;

      errorPositions.push({
        line: lineIndex,
        startPos,
        endPos,
        text: errorText,
        id: errorText,
      });

      processedChars += 4;
    }

    cleanLine = line.replace(/<<([^>]+)>>/g, '$1');
    parsedLines.push(cleanLine);
  });

  return {
    ...question,
    parsedCode: parsedLines,
    errorPositions,
  };
};