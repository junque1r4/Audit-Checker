# 🔍 Audit File Item Remover

Hey there! 👋 This script helps you remove specific items from your audit files without messing things up.

## 🤔 What does it do?

It's pretty simple:
- Finds and removes `<item>` or `<custom_item>` blocks from your audit files
- You can remove items by their description or name
- Keeps a backup of your file (just in case! 🔒)

## 📋 How to use it?

1. Make sure you have your audit file ready (like `your_file.audit`)

2. The easiest way to use it:
```python
# Remove stuff by description
find_and_remove_items("your_file.audit",
    descriptions=["Your description here"])

## 🌟 Cool Features

- 💾 Always creates a backup (filename.audit.backup)
- ✨ Cleans up empty spaces automatically
- 🔍 Prints items before and after removal so you can check
- 🛡️ Won't break your file structure

## 📝 Example

Let's say you want to remove an item with this description:
```
"6.2.6 Ensure no duplicate user names exist"
```

Just do:
```python
find_and_remove_items("your_file.audit",
    descriptions=["6.2.6 Ensure no duplicate user names exist"])
```

That's it! The script will:
1. 💾 Make a backup
2. 🔍 Find the item
3. ✂️ Remove it
4. 🎉 Show you what it did

## ⚠️ Need Help?

If something's not working:
1. Check if your file path is correct
2. Make sure the description/name matches exactly
3. Look at the backup file to see what changed
4. Cry

## 💡 Pro Tip

1. Use `print_all_items("your_file.audit")` to see all items in your file before removing anything!
2. Create a file with all the checks that you want to remove and give to the function as argument

## 🏆 TODO:
1. List ALL the checks and return numbers to the user select what he want to delete.
2. Add new checks to the list so that way you can add missing files
3. Add a option to modify a check

---
Made with ❤️ to make your audit file editing easier!
