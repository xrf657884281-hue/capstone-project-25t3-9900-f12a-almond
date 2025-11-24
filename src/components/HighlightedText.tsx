import React from 'react';

interface HighlightedTextProps {
  text: string;
  errors: string[];
  className?: string;
}

interface HighlightSegment {
  text: string;
  isError: boolean;
  errorType?: string;
}

export const HighlightedText: React.FC<HighlightedTextProps> = ({ 
  text, 
  errors, 
  className = "" 
}) => {
  // Extract error keywords and phrases
  const extractErrorKeywords = (errors: string[]): string[] => {
    const keywords: string[] = [];
    
    errors.forEach(error => {
      // Extract dates (years) - focus on incorrect years
      const yearMatches = error.match(/\b(18|19|20)\d{2}\b/g);
      if (yearMatches) {
        keywords.push(...yearMatches);
      }
      
      // Extract specific error information
      if (error.toLowerCase().includes('factual inaccuracy')) {
        // Extract specific inaccuracy
        const matches = error.match(/The (.*?) was (.*?) not (.*?)[\.]/i);
        if (matches) {
          keywords.push(matches[1]); // Subject
          keywords.push(matches[2]); // Error info
        }
        
        // Extract error info after "not"
        const notMatches = error.match(/not ([^\.]+)/i);
        if (notMatches) {
          keywords.push(notMatches[1].trim());
        }
      }
      
      if (error.toLowerCase().includes('logical inconsistency')) {
        // Extract logically inconsistent parts
        const matches = error.match(/The (.*?) would (.*?) making (.*?)[\.]/i);
        if (matches) {
          keywords.push(matches[1]);
        }
        
        // Extract "predates" related info
        const predatesMatch = error.match(/predates ([^\.]+)/i);
        if (predatesMatch) {
          keywords.push(predatesMatch[1].trim());
        }
      }
      
      // Extract quoted content
      const quotedMatches = error.match(/"([^"]+)"/g);
      if (quotedMatches) {
        keywords.push(...quotedMatches.map(q => q.replace(/"/g, '')));
      }
      
      // Extract specific error descriptions
      if (error.includes('built in')) {
        const builtMatches = error.match(/built in (\d{4})/i);
        if (builtMatches) {
          keywords.push(builtMatches[1]);
        }
      }
      
      // Extract specific locations, people, event names (avoid over-highlighting)
      const nameMatches = error.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g);
      if (nameMatches) {
        // Only take important names, avoid common words
        const importantNames = nameMatches.filter(name => 
          name.length > 3 && 
          !['The', 'This', 'That', 'Factual', 'Logical', 'Inconsistency', 'Inaccuracy'].includes(name)
        );
        keywords.push(...importantNames.slice(0, 2));
      }
    });
    
    return [...new Set(keywords)].filter(keyword => keyword.length > 1);
  };

  // Split text into highlighted and non-highlighted segments
  const createHighlightSegments = (text: string, errorKeywords: string[]): HighlightSegment[] => {
    if (errorKeywords.length === 0) {
      return [{ text, isError: false }];
    }

    const segments: HighlightSegment[] = [];
    let lastIndex = 0;

    // Find all error keyword positions
    const errorPositions: Array<{ start: number; end: number; keyword: string }> = [];
    
    errorKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      let match;
      while ((match = regex.exec(text)) !== null) {
        errorPositions.push({
          start: match.index,
          end: match.index + match[0].length,
          keyword: match[0]
        });
      }
    });

    // Sort by position and merge overlapping intervals
    errorPositions.sort((a, b) => a.start - b.start);
    const mergedPositions: Array<{ start: number; end: number; keywords: string[] }> = [];
    
    errorPositions.forEach(pos => {
      if (mergedPositions.length === 0 || mergedPositions[mergedPositions.length - 1].end < pos.start) {
        mergedPositions.push({
          start: pos.start,
          end: pos.end,
          keywords: [pos.keyword]
        });
      } else {
        const last = mergedPositions[mergedPositions.length - 1];
        last.end = Math.max(last.end, pos.end);
        if (!last.keywords.includes(pos.keyword)) {
          last.keywords.push(pos.keyword);
        }
      }
    });

    // Create segments
    mergedPositions.forEach(pos => {
      // Add normal text before error
      if (pos.start > lastIndex) {
        segments.push({
          text: text.slice(lastIndex, pos.start),
          isError: false
        });
      }
      
      // Add error text
      segments.push({
        text: text.slice(pos.start, pos.end),
        isError: true,
        errorType: pos.keywords.join(', ')
      });
      
      lastIndex = pos.end;
    });

    // Add remaining normal text
    if (lastIndex < text.length) {
      segments.push({
        text: text.slice(lastIndex),
        isError: false
      });
    }

    return segments;
  };

  const errorKeywords = extractErrorKeywords(errors);
  const segments = createHighlightSegments(text, errorKeywords);

  return (
    <div className={`whitespace-pre-wrap break-words ${className}`}>
      {segments.map((segment, index) => (
        <span
          key={index}
          className={segment.isError ? 'bg-red-200 text-red-900 border-b-2 border-red-400 font-semibold px-1 rounded-sm' : ''}
          title={segment.isError ? `Error: ${segment.errorType}` : undefined}
        >
          {segment.text}
        </span>
      ))}
    </div>
  );
};
