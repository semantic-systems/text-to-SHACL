import time

from openai import OpenAI

# API configuration
api_key = 'cc0637db9153801f5d4b158dbb9f504f'  # Replace with your API key
base_url = "https://chat-ai.academiccloud.de/v1"
available_models = ["meta-llama-3.1-8b-instruct", "meta-llama-3.1-70b-instruct",
                    "llama-3.1-sauerkrautlm-70b-instruct",
                    "mistral-large-instruct",
                    "qwen2.5-72b-instruct",
                    "codestral-22b"]

model = available_models[4]  # Choose any available model

# Start OpenAI client
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# Get response
start_time = time.time()
chat_completion = client.chat.completions.create(
    messages=[{"role": "system", "content": "You are a helpful assistant"},
              {"role": "user", "content": "This area formed the heart of the plantation of Bernard Xavier Philippe de Marigny de Mandeville, who lived in a mansion where the electrical substation now stands. Expecting that the Louisiana Purchase would spur urban expansion, Marigny had his parcel subdivided for urbanization in 1805, hiring French engineer Nicolas de Finiels to design a plat. Finiels successfully reconciled an extension of the French Quarter street grid with a sharp bend of the Mississippi River by reshaping key connector squares into polygons of various configurations, which surveyor Barthelemy Lafon then laid out in 1806. The first neighborhood downriver from the city proper, the Faubourg Marigny soon developed into a predominantly Creole community, including substantial numbers of both Free People of Color, as well as enslaved African Americans and German, Irish and other immigrant populations. A century later, these riverfront blocks hosted a variety of light industrial land uses worked by the neighborhood’s blue-collar residents. The four blocks surrounding this intersection were occupied in the early 1900s by rice mills, an ice plant, horse and mule stables, a yarn and hosiery factory and a streetcar barn; the streets themselves were paved in granite stones. Originally named Rue d’Enghein, the street was later called Lafayette and then Almonaster before finally being named Franklin. This avenue marked the lower limit of the Marigny Plantation and of the original faubourg, despite that current perception places the neighborhood’s lower border at Press Street. The area below Franklin was subdivided after 1810 as the Faubourg D’Aunoy and soon developed a similar cultural milieu as its neighbor. The imposing lavender building overlooking the Chartres/Franklin intersection was once a Methodist church, and the restaurant across the street is said to incorporate circa-1790s structural elements from the D’Aunoy plantation complex. Royal Street heading upriver: This stretch of Royal Street, formerly Rue Casa Calvo, is quintessential Faubourg Marigny. Of particular interest is 2231 Royal, a one-of-a-kind 1830s townhouse with a central carriageway and raised basement, as well as the two solid circa-1850s Greek Revival structures on either side of the Elysian Fields intersection. Royal Street was the return route of the “streetcar named Desire,” after it rolled down Bourbon and Dauphine streets to Desire Street in present-day Bywater. Electricity for the streetcar system in these lower neighborhoods came from the brick edifice at the foot of Elysian Fields, known in the early 1900s as the New Orleans Railways and Light Company Claiborne Power House. Years before the Marigny family came into possession of this land, it was owned by Claude Joseph Villars Dubreuil, a French colonial builder in constant need of lumber. In the 1740s, Dubreuil had a diversion canal excavated from the levee through the center of his parcel, to power a sawmill with the flow of river water. Dubreuil’s canal later became the Marigny Canal, and when Finiels designed his street grid in 1805, he used this pre-existing axis to serve as the subdivision’s grand avenue, giving it great width, an adjacent park (Washington Square), and a lovely name, Champs-Élysées . In 1831, Elysian Fields became the right-of-way for the track bed of the Pontchartrain Railroad, the first to complete its charter west of the Appalachians. Known locally as “Smoky Mary,” the steam line operated until 1932. Royal Street at Washington Square: Into the 1960s, the river side of this block was home to Holy Redeemer Church, a black Catholic congregation worshipping in a circa-1860 edifice originally designed as the Third Presbyterian Church by architects Albert Diettel and Henry Howard. Next door, on the corner of Frenchmen Street, was a Carnegie Library built in 1902. All this changed when Hurricane Betsy utterly destroyed the church and damaged the library. Five years later, in 1970, the cleared lot became home to the Christopher Inn, a project of the Archdiocese’s nonprofit housing agency created by Archbishop Phillip Hannan for elderly congregants. The building’s large scale and International Style have raised the ire of historicists ever since, but the apartments provide affordable downtown living for senior citizens, many of whom grew up in the neighborhood and would otherwise be unable to live here."
                                          "\n \n Count words. "}],
    model=model,
    temperature=0.7,
    top_p=0.8
)
print(f"Time taken: {time.time() - start_time:.2f} seconds")

# Print full response as JSON
# You can extract the response text from the JSON object
print(chat_completion.choices[0].message.content)