## [!] Still in development! Do not try using this until a stable release has been made.
## The documentation might change for later versions!

# bazeb00rd
bazeb00rd is a Python script to make communications with the Wii Balance Board, using PyBlueZ

## Why?
With bazeb00rd you can integrate your games with the Wii Balance Board, or just use it for fun!

## Usage:
```python
import bazeb00rd as boord  # Module name will change.

wb = boord.Boord()
address = wb.discover(6)
wb.connect(address)

report = wb.report()
print(report["total_weight"])
```
This is just a concept, the development is still ongoing, everything might differ.

## Status:
```
? | Connection
? | Calibration
? | Getting data
```

## Thanks:
* [gr8w8upd8m8](https://github.com/skorokithakis/gr8w8upd8m8) and [wiiboard](https://github.com/PierrickKoch/wiiboard), inspiring me to create my own api-ish thing and helping me understand how they handle the inputs (Both of them fail with the current Python)

* That one customer of my father who got me a Wii or something idk that's why I'm a nerd now