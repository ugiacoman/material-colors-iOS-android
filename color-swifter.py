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
			uicolor = "{} = UIColor(red:{}, green:{}, blue:{}, alpha:1.0) // {}\n".format(shadeName, r, g, b, hex)
			uiColorsArray.append(uicolor)

	uiColorsArray = sorted(uiColorsArray)

	for i, item in enumerate(uiColorsArray):
		uiColorsArray[i] = "    var " + item

	return uiColorsArray

'''
createFile
---------
Creates colors.swift, saves to directory where script is located
'''

def createFile(colorsArray):


	file = open("MaterialColors.swift", "w")
	file.write("struct MaterialColors {\n")
	for item in colorsArray:
		file.write(item)
	file.write("}")


def main():
	page = downloadSource()
	# key value of all colors {color: {uicolor: "", Hex: ""}}
	colors = parsePage(page)
	createFile(colors)

if __name__ == "__main__":
    # execute only if run as a script
    main()