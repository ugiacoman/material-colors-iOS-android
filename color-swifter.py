from bs4 import BeautifulSoup
import requests


lowerMe = lambda s: s[:1].lower() + s[1:] if s else ''

'''
downloadSource
--------------
Scrapes https://material.google.com/style/color.html#color-color-palette
'''
def downloadSource():
	r = requests.get('https://material.google.com/style/color.html#color-color-palette')
	return r.text


'''
parsePage
---------
Parses page to create Dictionary of Colors 
Ex: {mainColor: {'shade': 'hex'}, ... }
'''
def parsePage(page):
	colorDict = {}
	uiColorsArray = []
	xmlArray = []

	mainColor = ""
	shadesArray = []
	hexArray = []	
	

	soup = BeautifulSoup(page, "html.parser")
	colorGroups = soup.find_all("section", class_="color-group")

	for group in colorGroups:

		# Get Key
		name = group.find_all("span", class_="name")
		color = group.find_all("span", class_="shade")
		hexValue= group.find_all("span", class_="hex")

		for n in name:
			mainColor = str(n.text.strip())

		for c in color:
			shadesArray.append(str(c.text.strip()))
		for h in hexValue:
			hexArray.append(str(h.text.strip()))

		colorDict[mainColor] = dict(zip(shadesArray, hexArray))

	

	for mainColor in colorDict:
		for shade in colorDict[mainColor]:
			shadeName = mainColor.replace(" ", "") + shade
			shadeName = lowerMe(shadeName)
			hex = colorDict[mainColor][shade]
			r = round(float(int(hex[1:3], 16)) / 255, 2)
			g = round(float(int(hex[3:5], 16)) / 255, 2)
			b = round(float(int(hex[5:7], 16)) / 255, 2)
			uicolor = '{}() -> UIColor {{\n        return UIColor(red:{}, green:{}, blue:{}, alpha:1.0) // {}\n    '\
					  '}}\n\n'.format(shadeName, r, g, b, hex)
			xml = '{}">{} </color>\n'.format(shadeName, hex)
			uiColorsArray.append(uicolor)
			xmlArray.append(xml)

	uiColorsArray = sorted(uiColorsArray)
	xmlArray = sorted(xmlArray)

	for i, (uicolor, xml) in enumerate(zip(uiColorsArray, xmlArray)):
		uiColorsArray[i] = "    class func " + uicolor
		xmlArray[i] = '  <color name="' + xml

	return [uiColorsArray,xmlArray]

'''
createFile
---------
Creates MaterialColors.swift and colors.xml, saves to directory where script is located
'''

def createFile(colorsArray):

	# Create swift file
	file = open("MaterialColors.swift", "w")
	file.write("import UIKit\n\nextension UIColor {\n")
	for item in colorsArray[0]:
		file.write(item)
	file.write("}")

	# Create xml file
	file = open("colors.xml", "w")
	file.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')
	for item in colorsArray[1]:
		file.write(item)
	file.write("</resources>")


def main():
	page = downloadSource()
	# key value of all colors {color: {uicolor: "", Hex: ""}}
	colors = parsePage(page)
	createFile(colors)

if __name__ == "__main__":
    # execute only if run as a script
    main()