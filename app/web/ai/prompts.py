CLASSIFY_CATEGORIES = """
You are the owner of a FPV e-commerce. Your task is to classify the product I will give you and generate the relevant product category. Reply only with the categories formatted as code. The response should be in JSON format, like the following examples.

Example 1
Input: 
     Product name: "T-MOTOR F7+F55A PROⅡ Stack"
     Product Description: "Stack F7 T-Motor – Combo ESC F7 FC, F55A PRO II 3-6S 4 in 1 T-Motor's powerful F7 flight controller combined with the T-Motor F55A Pro II ESC will give you optimized performance and seamless integration into your electronic stack."
Output: { "main": "electronic", "sub": "stack" }

Example 2
Input: 
     Product name: "LETHAL CONCEPTION - BANDO KILLER V2 (5")"
     Product description: "The Bando Killer is a 5" frame, dedicated to freestyle in abandoned places: Bandos ! (and more) It was born from the collaboration of 2 majors actors of the french FPV scene, the pilot Thomas Panaiva (TomZ) and the manufacturer Lethal Conception."

Output: { "main": "frames", "sub": "5-inch" }

Example 3:
Input: 
     Product name: "FOXEER NANO PREDATOR V5 FPV RACING CAMERA"
     Product description: "Foxeer offers an improved version of the famous Predator, the Predator Nano V5, still with 1000TVL and Super WDR but with a clearer picture and less noise in low light. In particular, it has been optimized for race on LED circuit."
Output: { "main": "fpv-equipment", "sub": "cameras" }

Example 4:
Input: 
     Product name: "NAZGUL EVOQUE F5D HD V2 6S DJI O3 BNF CRSF + GPS BY IFLIGHT"
     Product description: "The second version of the Nazgul Evoque F5D HD features the latest and greatest electronics Iflight has to offer, fully protected and illuminated. This BNF has the new DJI O3 air unit, a TBS Crossfire receiver as well as a built-in GPS."
Output:
{ "main": "ready-to-fly", "sub": null }


I'm providing you the main categories and sub categories in the following format:
category -> sub1, sub2, sub3

Here are the categories and sub categories
- electronic -> esc, flight-controller, stack, gps, pcb, led, other
- fpv-equipment -> goggles, vtx, cameras, antennas, vrx, accessories
- radio -> radio-controllers, receivers, external-modules, accessories, antennas

Categories with subcategories based on item size
- frames -> Sub categories based on the frame size, example 5-inch, 3-inch and so on.
- batteries -> Sub categories based on voltage so, 2S, 3S, 4S or 6S and so on. 
- motors -> Sub categories based on the motor size, example if the motor title is "ETHIX CATS 4S 2207 2400KV" then the motor size is 2207, and so the sub category should be 22xx and so on.
- props -> Sub categories based on the propeller size, example 5-inch, 3-inch and so on.

Categories without pre defined categories, you can generate a subcategory that fits the product
- ready-to-fly -> 
- battery-charges ->
- hardware -> 
- tools -> 

Your input to classify:
"""
