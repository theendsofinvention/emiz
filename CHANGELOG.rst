Changelog
=========
(unreleased)
------------
Fix
~~~
- Fix visibility in weather report. [132nd-etcher]
Other
~~~~~
- Remove unused values. [132nd-etcher]
  pep8 [auto]
  sorting imports [auto]
  update requirements [auto]
0.1.24 (2018-01-28)
-------------------
New
~~~
- Add test mission for DCS 1.5.8 (#6) [132nd-etcher]
0.1.24a1 (2018-01-28)
---------------------
Fix
~~~
- Fix forced temperature not applied in case of snow/snow storm. [132nd-
  etcher]
0.1.24a3 (2018-01-28)
---------------------
New
~~~
- Add test mission for DCS 1.5.8. [132nd-etcher]
0.1.22 (2018-01-23)
-------------------
Fix
~~~
- Fix visibility in METAR from mission in case of fog. [132nd-etcher]
0.1.21 (2018-01-23)
-------------------
Fix
~~~
- Fix issue with unwanted fog. [132nd-etcher]
0.1.18 (2017-12-27)
-------------------
Fix
~~~
- Fix bug in mission.day. [132nd-etcher]
- Fix issue with cloud height in METARs inferred from MIZ files. [132nd-
  etcher]
  fix #3
- Fix bug where fog would not be disabled from a mission. [132nd-etcher]
Other
~~~~~
- Fix re-introduced basic datetime func. [132nd-etcher]
0.1.14 (2017-12-24)
-------------------
New
~~~
- AVWX metar to speech. [132nd-etcher]
- Add AVWX API. [132nd-etcher]
Changes
~~~~~~~
- Fix intro line for ATIS. [132nd-etcher]
- Change ATIS intro speech. [132nd-etcher]
Fix
~~~
- Replace "altimeter" with "Q N H" [132nd-etcher]
- Fix init. [132nd-etcher]
- Fix clouds when applying metar to miz file. [132nd-etcher]
0.1.13 (2017-12-17)
-------------------
Fix
~~~
- Fix issue when no clouds were present. [132nd-etcher]
0.1.12 (2017-10-04)
-------------------
New
~~~
- Added custom METAR class to handle printing pressure with all units.
  [132nd-etcher]
0.1.11 (2017-10-04)
-------------------
New
~~~
- Added custom METAR class to handle printing pressure with all units.
  [132nd-etcher]
0.1.8 (2017-08-27)
------------------
Fix
~~~
- Catch OSError while editing MIZ file. [132nd-etcher]
0.1.6 (2017-08-26)
------------------
Changes
~~~~~~~
- Using edit_miz for batch operations. [132nd-etcher]
Fix
~~~
- Remove CLRXXXX from metar string while parsing. [132nd-etcher]
0.1.5 (2017-08-26)
------------------
Fix
~~~
- Catch ParserError while parsing for metar string. [132nd-etcher]
0.1.4 (2017-08-24)
------------------
- Add mission time. [132nd-etcher]
0.1.3 (2017-08-20)
------------------
- Update changelog. [132nd-etcher]
- Pep8 formatting. [132nd-etcher]
- Remove unused module. [132nd-etcher]
- Move weather in package, add METAR builder and a few tests. [132nd-
  etcher]
0.1.2 (2017-08-20)
------------------
- Update changelog. [132nd-etcher]
- Update requirements. [132nd-etcher]
- Export _set_weather. [132nd-etcher]
0.1.1 (2017-08-19)
------------------
- Add MissionWeather to exports. [132nd-etcher]
- Dev: initial commit. [132nd-etcher]
0.1.0 (2017-08-19)
------------------
- Initial commit. [132nd-etcher]