**[中文](README-cn.md)**
# Mini Project (20250310 Created)

## Operational Steps
**Extract**
Write unit codes in `unit_codes.txt`, e.g:

`AERO3360`  
`AERO3261`  
`AMME3500`  

Save, then run `collector`, `collector` will generate `task_info.html` for user to read immediately.
**Check Due**
Make sure you already runned `collector` or `task_info.html` exists. Run `due`, and it will write next 7 days dues into `due.html`, include `Multiple weeks` type assessments.


## Remaining Description (Just record developed process and files property)

### Background
Students always confused what units and assessments they will do in a new semester. In general, USYD student will learn 4 units (24 credit points) in a semester. If students want to make a clear plan, they will spend much time to serach every units web to found it.

### Program Description
This program can help USYD student to extract all units' assessments in `2025S1`, and generate as a `html` file that student can read conveniently. Meanwhile can help student to check dues in the next 7 days.

### Files Description
`collector.py`: Extractor (High efficiency and low storage)
`due.py`: Extract next 7 days due

### Updated record
**2025.03.10**
1. Implement the most basic scanning of the form and read it.

**2025.03.11**
1. Improve the table reading format and add `html` format as the reading version.
2. Add window display for reading progress.

**2025.03.13**
1. Significantly improve the entire reading method, and the efficiency is expected to increase by 3 times.
2. The file is overall lightweight and occupies less space.