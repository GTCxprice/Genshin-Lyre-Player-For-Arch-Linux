using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Melanchall.DryWetMidi.Core;
using Melanchall.DryWetMidi.Interaction;
using System.Collections.Generic;

class Program
{
    // Explicit MIDI note to Lyre key mapping
    static readonly Dictionary<int, string> noteToKey = new Dictionary<int, string>()
    {
        {48,"z"}, {50,"x"}, {52,"c"}, {53,"v"}, {55,"b"}, {57,"n"}, {59,"m"},
        {60,"a"}, {62,"s"}, {64,"d"}, {65,"f"}, {67,"g"}, {69,"h"}, {71,"j"},
        {72,"q"}, {74,"w"}, {76,"e"}, {77,"r"}, {79,"t"}, {81,"y"}, {83,"u"}
    };

    static async Task Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.WriteLine("Usage: dotnet run -- <file.mid>");
            return;
        }

        var file = MidiFile.Read(args[0]);
        var tempoMap = file.GetTempoMap();
        var notes = file.GetNotes();

        // Convert notes to (timeMs, note)
        var eventsList = new List<(long timeMs, int note)>();
        foreach (var note in notes)
        {
            var mt = TimeConverter.ConvertTo<MetricTimeSpan>(note.Time, tempoMap);
            eventsList.Add(((long)mt.TotalMilliseconds, note.NoteNumber));
        }

        // Sort by time
        eventsList.Sort((a, b) => a.timeMs.CompareTo(b.timeMs));

        // Improved timing loop
        var stopwatch = Stopwatch.StartNew();
        int index = 0;

        while (index < eventsList.Count)
        {
            long elapsed = stopwatch.ElapsedMilliseconds;

            // Send all notes whose time has come
            while (index < eventsList.Count && eventsList[index].timeMs <= elapsed)
            {
                var key = MapNoteToKey(eventsList[index].note);
                if (key != null)
                    SendKey(key);

                index++;
            }

            // Sleep a tiny bit to avoid 100% CPU
            await Task.Delay(1);
        }
    }

    // Map MIDI note to Genshin Lyre key using explicit dictionary
    static string MapNoteToKey(int midiNote)
    {
        return noteToKey.TryGetValue(midiNote, out var key) ? key : null;
    }

    // Send keypress using xdotool
    static void SendKey(string key)
    {
        Process.Start(new ProcessStartInfo
        {
            FileName = "xdotool",
            Arguments = $"key --clearmodifiers {key}",
            UseShellExecute = false
        });
    }
}
