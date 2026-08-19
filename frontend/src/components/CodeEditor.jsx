import React from 'react';
import Editor from '@monaco-editor/react';
import { useTheme } from '../context/ThemeContext';
import LoadingSpinner from './LoadingSpinner';

export default function CodeEditor({
  value,
  onChange,
  language = 'python',
  readOnly = false,
  height = '420px',
}) {
  const { isDark } = useTheme();

  return (
    <div
      style={{
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        background: isDark ? '#1e1e1e' : '#fffffe',
      }}
    >
      <Editor
        height={height}
        language={language}
        value={value}
        theme={isDark ? 'vs-dark' : 'light'}
        onChange={(val) => onChange && onChange(val || '')}
        loading={<LoadingSpinner message="Loading Monaco Code Editor..." />}
        options={{
          readOnly: readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "'JetBrains Mono', Consolas, 'Courier New', monospace",
          lineNumbers: 'on',
          roundedSelection: false,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          insertSpaces: true,
          wordWrap: 'on',
          padding: { top: 12, bottom: 12 },
        }}
      />
    </div>
  );
}
