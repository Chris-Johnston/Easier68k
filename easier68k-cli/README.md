### usage:

This requires that easy68k is installed on the system to work.

```
python3 ./cli.py
(easier68k) assemble ./test.68k
[ stuff gets printed ]

(easier68k) assemble ./test.68k ./output.json
[ file saved ]
[ errors/warnings printed ]


(easier68k) run ./output.json
[ will load sub-repl eventually ]

(easier68k) exit
```

note: on Linux (and other operating systems?) auto complete works when pressing tab
