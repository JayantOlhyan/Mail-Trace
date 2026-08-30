'use client';

import React, { useState } from 'react';
import { AnalystNote } from '@/types';
import { MessageSquare, Plus, User, Clock } from 'lucide-react';
import { api } from '@/lib/api';

interface AnalystNotesProps {
  entityType: string;
  entityId: string;
  initialNotes?: AnalystNote[];
}

export function AnalystNotes({ entityType, entityId, initialNotes = [] }: AnalystNotesProps) {
  const [notes, setNotes] = useState<AnalystNote[]>(initialNotes);
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      const newNote = await api.addAnalystNote(entityType, entityId, content.trim());
      setNotes((prev) => [newNote, ...prev]);
      setContent('');
    } catch (err) {
      console.error('Failed to save note:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-indigo-400" />
          Analyst Investigation Notes & Assessment Log
        </h3>
        <span className="text-xs font-mono text-slate-400">
          {notes.length} {notes.length === 1 ? 'Entry' : 'Entries'}
        </span>
      </div>

      {/* Input Form */}
      <form onSubmit={handleAddNote} className="space-y-2">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={`Add investigative observations or case notes for ${entityType} ${entityId}...`}
          rows={3}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting || !content.trim()}
            className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold font-mono disabled:opacity-50 transition"
          >
            <Plus className="w-4 h-4" />
            <span>{isSubmitting ? 'Saving Note...' : 'Record Analyst Note'}</span>
          </button>
        </div>
      </form>

      {/* Notes List */}
      <div className="space-y-3 pt-2">
        {notes.length === 0 ? (
          <p className="text-xs text-slate-500 font-mono text-center py-4 bg-slate-950/50 rounded-lg border border-slate-800/50">
            No analyst notes added to this entity yet.
          </p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="flex items-center space-x-1.5 text-indigo-300 font-semibold">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  <span>{note.author}</span>
                </span>
                <span className="flex items-center space-x-1 text-slate-500 text-[11px]">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(note.timestamp).toLocaleString()}</span>
                </span>
              </div>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">{note.content}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
