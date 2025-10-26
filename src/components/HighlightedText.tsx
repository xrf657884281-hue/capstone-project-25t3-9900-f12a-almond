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
  // 提取错误关键词和短语
  const extractErrorKeywords = (errors: string[]): string[] => {
    const keywords: string[] = [];
    
    errors.forEach(error => {
      // 提取日期（年份）- 特别关注错误的年份
      const yearMatches = error.match(/\b(18|19|20)\d{2}\b/g);
      if (yearMatches) {
        keywords.push(...yearMatches);
      }
      
      // 提取具体的错误信息
      if (error.toLowerCase().includes('factual inaccuracy')) {
        // 提取具体的不准确信息
        const matches = error.match(/The (.*?) was (.*?) not (.*?)[\.]/i);
        if (matches) {
          keywords.push(matches[1]); // 主题
          keywords.push(matches[2]); // 错误信息
        }
        
        // 提取 "not" 后面的错误信息
        const notMatches = error.match(/not ([^\.]+)/i);
        if (notMatches) {
          keywords.push(notMatches[1].trim());
        }
      }
      
      if (error.toLowerCase().includes('logical inconsistency')) {
        // 提取逻辑不一致的部分
        const matches = error.match(/The (.*?) would (.*?) making (.*?)[\.]/i);
        if (matches) {
          keywords.push(matches[1]);
        }
        
        // 提取 "predates" 相关信息
        const predatesMatch = error.match(/predates ([^\.]+)/i);
        if (predatesMatch) {
          keywords.push(predatesMatch[1].trim());
        }
      }
      
      // 提取引号中的内容
      const quotedMatches = error.match(/"([^"]+)"/g);
      if (quotedMatches) {
        keywords.push(...quotedMatches.map(q => q.replace(/"/g, '')));
      }
      
      // 提取具体的错误描述
      if (error.includes('built in')) {
        const builtMatches = error.match(/built in (\d{4})/i);
        if (builtMatches) {
          keywords.push(builtMatches[1]);
        }
      }
      
      // 提取具体的地点、人物、事件名称（但避免过多高亮）
      const nameMatches = error.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g);
      if (nameMatches) {
        // 只取重要的名称，避免常见词汇
        const importantNames = nameMatches.filter(name => 
          name.length > 3 && 
          !['The', 'This', 'That', 'Factual', 'Logical', 'Inconsistency', 'Inaccuracy'].includes(name)
        );
        keywords.push(...importantNames.slice(0, 2));
      }
    });
    
    return [...new Set(keywords)].filter(keyword => keyword.length > 1);
  };

  // 将文本分割为高亮和非高亮片段
  const createHighlightSegments = (text: string, errorKeywords: string[]): HighlightSegment[] => {
    if (errorKeywords.length === 0) {
      return [{ text, isError: false }];
    }

    const segments: HighlightSegment[] = [];
    let currentIndex = 0;
    let lastIndex = 0;

    // 找到所有错误关键词的位置
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

    // 按位置排序并合并重叠的区间
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

    // 创建片段
    mergedPositions.forEach(pos => {
      // 添加错误前的正常文本
      if (pos.start > lastIndex) {
        segments.push({
          text: text.slice(lastIndex, pos.start),
          isError: false
        });
      }
      
      // 添加错误文本
      segments.push({
        text: text.slice(pos.start, pos.end),
        isError: true,
        errorType: pos.keywords.join(', ')
      });
      
      lastIndex = pos.end;
    });

    // 添加最后的正常文本
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
          title={segment.isError ? `错误: ${segment.errorType}` : undefined}
        >
          {segment.text}
        </span>
      ))}
    </div>
  );
};
