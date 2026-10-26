## Additional `conda` commands

I faced the problem that installed env manager `miniconda` runs in `bash` but fails to run in `zsh`. To fix it, I needed to figure out where `conda`
lives in the memory of my laprop:
```bash
which conda || find ~name "conda" -type f 2>/dev/null
>> returns [conda path]
```

and which version of `conda` I have:
```bash
[conda path] --version
>> returns version [conda 26.5.3]
```

Since I now know, where the `conda` is, I can initialize it for any shell:
`[path] init zsh`

Reopen the shell.
Done.
