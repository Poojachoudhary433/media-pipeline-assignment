---
title: "Python Automation Project: File Organizer"
author: "Your Name"
date: "2025-12-31"
duration: "10 min"
---

# Slide 0
## Building a File Organizer using Python
**Subtitle:** A Simple Python Automation Project 

![img](images/Intro.jpg)  
**Duration:** 1 min

---

# Slide 1
## Introduction 
-  Hello everyone 👋  
- I am a Python Developer Intern
- In this video,I will demonstrate a simple **Python automation project**  
that helps organize files automatically.

Automation is one of the most powerful uses of Python,  
and this project shows how we can use it in real life.


**Duration:** 1 min

---

# Slide 2
## Problem Statement
Our download or desktop folder often becomes messy  
with files like:

- PDFs  
- Images  
- Videos  
- Documents  

Manually organizing them takes time.

So the problem is:
👉 **Can we automate file organization using Python?**

The answer is **YES!**


**Duration:** 1 min

---

# Slide 3
## Python Concepts Used

In this project, we use:

- `os` module  
- `shutil` module  
- File extensions  
- Conditional statements  

These concepts help Python interact  
directly with the operating system.

**Duration:** 2 min

---

# Slide 4
## Project Logic

1. Select the target folder  
2. Read all files from the folder  
3. Check file extensions  
4. Create folders if not present  
5. Move files into respective folders  

This logic runs automatically  
with a single Python script.



**Duration:** 2 min

---

# Slide 5
##  Python Code: File Organizer

```python
import os
import shutil

path = "C:/Users/YourName/Downloads"

files = os.listdir(path)

for file in files:
    filename, extension = os.path.splitext(file)

    if extension == "":
        continue

    extension = extension[1:]

    folder_path = os.path.join(path, extension)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    shutil.move(
        os.path.join(path, file),
        os.path.join(folder_path, file)
    )

print("Files organized successfully!") 



**Duration:** 4 min

---

# Slide 6
## Conclusion

In this video, we learned:

- How Python automates tasks  
- How to organize files using code  
- Practical use of os and shutil modules  

Automation makes Python extremely powerful.

Thank you for watching! 🙏


**Duration:** 1 min

---


# Slide 7
# Thank You
## Happy Coding 🚀
**Thank you for watching!**  
- Any questions?  
- Contact: your.email@example.com  

![Thank You Image](images/Thank_you.jpg)  <!-- Optional decorative image -->

**Duration:** 1 min

