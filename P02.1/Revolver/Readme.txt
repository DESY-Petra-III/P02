Created by: Martin Domaracky
Modified:   26.10.2013

Q: How to compile QT .ui (User interface file) file into .py file?
A: taurusuic4 /path/to/file.ui > /path/to/file.py
   or pyuic4 /path/to/file.ui > /path/to/file.py
   
Q: How to compile QT .qrc (resource file) file into .py file?
A: pyrcc4 /path/to/file.qrc -o /path/to/file.py

Q: How to generate documentation
A: epydoc --html /path/to/Revolver -o /path/to/Revolver/Doc/ --graph classtree -v

Q: Revolver library or Revolver.classes library was not found error
A: add module path into standard library paths
   for linux users:
	   If you're using bash (on a Mac or GNU/Linux distro), add this to your ~/.bashrc
	   export PYTHONPATH=$PYTHONPATH:/path/to/Revolver/ParentDir
	   then run: source ~/.bashrc
   for windows users:
   	   My Computer > Properties > Advanced System Settings > Environment Variables >
       Then under system variables I create a new Variable called PYTHONPATH. 
       In this variable specify Revolver parent dir path