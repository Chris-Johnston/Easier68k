# Easier68k (Development Branch)

Easier68k is a python library that assembles and simulates the Motorola 68k CPU Architecture.

## What's going on here?

The `dev` branch of easier68k contains a _full rewrite_ of the tool. The initial version
of the project lives in the `master` branch, and was the scope of the MVP for the project
(after all, this was a school assignment whose scope has massively spiraled out of control).
The MVP was built with non-scalable design patterns for each of the opcodes, this rewrite
in the `dev` branch is an effort to re-do things in a way that massively improves the experience
of extending Easier68k. (Adding opcodes used to take up many hundreds of LOC, some sections were copied a lot.)

The interface for the rewrite will be radically different. I'm dropping the CLI 'shell' thingy
since I didn't find it to be very useful. It will still be fully functional when called from the command
line, and it can also be imported to be integrated with other things as well. (There is a part of me which wishes that I had done this in C++ so it could be ported to literally anything under the sun.)

## Rewrite Status

The rewrite is now about as feature-complete as the `master` branch is.
There's still plenty to work on, though. There are already massive improvements
to the MVP with regard to scaling.

### Assembly and Disassembly
Disassembly of nearly all opcodes work. The "Assemblers" handle the templates which
slice data as necessary from the incoming memory, and are the same templates used
to serialize opcodes into memory.

There is an issue with multi-word opcodes and immediate data. The first option that
comes to me is that the Assemblers will have to be expanded to manage reading of
immediate data if it's specified by the opcode mode.
This is most necessary for the branch opcodes, as they all could look at the next
16 or 32 bits to determine their displacement.

### Parsing

This is one of the best changes from the initial version.

Parsing is a difficult job. This has now been outsourced to the Lark library
for which a grammar has been created. I didn't want to have to rewrite or salvage
the parsing logic from before (which from what I recall was pretty closely integrated
with everything else), and so it just made so much more sense to grab something off-the-shelf.

The grammar could be recycled for use with an editor plugin, but I'm fairly certain that there already is one for vscode.

### Namespaces

Trying to import things in the original version wasn't very nice. Things were super-nested, which looked nice in the file explorer but was a hassle in the editor.
This is one of the larger python projects I've worked on to date, but so far I'm going
ahead with a more flattened structure.

### Simulation

Simulation is kinda working. Like the old version, it's able to simulate
a very basic "Hello World" program with a small amount of branching. There are
still some gaps in the implementation.

One challenge I'm finding is that I need to determine a consistent way to determine the CCR bits. Python doesn't provide any fancy interface for doing more complex bit-wise operations more than the essentials as far as I know, so I still have
some work around wrapping normal operations like shifting, rotating, basic math, etc. to check for overflows and carries. This is currently done as part of the MemoryValue type, which probably could be named better. (That's another thing I'm unsure about, if it would be better to keep juggling between types everywhere, or if I could directly manipulate streams of bytes instead. 99% of the time I convert things into an unsigned int and manipulate on that, don't think byte operations would make that any easier. Would also be nice to stop flipping between ints and MemoryValues...)

As part of this, I also need some spring cleaning to remove all of my messy debug
statements. There's a lot. Would be nice to use a proper logger at some point.

### Tests

Hahahahahahaha.

The rewrite does not have unit tests, because the interface keeps changing.
I've mostly been testing with a short script which parses a file, disassembles it,
simulates it, etc.

This is on the radar for things to re-add. The MVP had great code coverage, but it's
just not viable to add tests when there are still fundamental changes that need to be
made first.

### dev notes / reference material

http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf

https://www.nxp.com/files-static/archives/doc/ref_manual/M68000PRM.pdf
