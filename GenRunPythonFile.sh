#!/bin/bash
for filename in `ls AllResults/*.so`;
do
	echo $filename
	module=$"`echo $filename | sed 's/AllResults\///' | sed 's/.so//'`"
	echo $module
	echo "import $module" > AllResults/RunPython$module.py
	echo "$module.main()" >> AllResults/RunPython$module.py
	echo "Complete RunPython$module.py!"
done
