import json
import ast

output_file = open('finalData.json', 'w')
review_file = open('yelp_academic_dataset_review.json', 'r')
business_file = open('yelp_academic_dataset_business.json', 'r')
restaurant_name = open('resturant.json', 'w')
"""
#final json will be a dic where the keys are a city and state (ex: "New York, NY")
#these keys then map to a new dic, where the keys are the restaurants names.
#the names map to a dic of the rest of the info about the restaurant (star rating,
#list of reviews, etc.)

EXAMPLE:
{"ITHACANY: {"PURITYICECREAM":{reviews:[], attributes:[], ...}, "COLLEGETOWNBAGELS":{...}},
"NEWYORKNY: {...},
"BOSTONMA: {...}}

#initialize new json, this will be one large json where the keys are the
#business_ids and the values are another dic of everything else
#i think this will make it easier to merge the reviews json and the business one
"""
json_merge = {}
#filter business file
#ne = ["MA"]
ne = ["BOSTON"]
star_range = [3.0,3.5,4.0,4.5,5.0]
for line in business_file:
  current_json = json.loads(line) #turns each individual json line into a dic
  #print(current_json)
  #categories = current_json["categories"]
  num_reviews = current_json["review_count"]
  star = current_json["stars"]
  #check it's a restaurant and has >= 5 reviews
  categories = current_json["categories"]
  state = current_json["state"]
  city = current_json["city"]
  name = current_json["name"]

  if (not categories is None) and ("Restaurants" in categories) and (num_reviews >= 5) and (city.upper() in ne) and (star in star_range) :
    id_dic = {}
    bus_id = current_json["business_id"]
    name = current_json["name"]
    # city = current_json["city"]
    # state = current_json["state"]
    #attributes = current_json["attributes"]
    #get name, city, state, and attributes into the dic
    id_dic["name"] = name
    id_dic["city"] = city
    id_dic["state"] = state
    #id_dic["attributes"] = attributes
    id_dic["ID"] = bus_id
    attribute = current_json["attributes"]
    if attribute is None:
      pricerange = 3
    else:
      if "RestaurantsPriceRange2" not in attribute:
        pricerange = 3
      else:
          pricerange = attribute["RestaurantsPriceRange2"]
    id_dic["price"] = pricerange
    if attribute is None:
      ambience = []
    else:
      if "Ambience" not in attribute:
        ambience = []
      elif attribute["Ambience"] == "None":
        ambience = []
      else:
          dic = attribute["Ambience"]
          temp = []
          my_dict = ast.literal_eval(dic)
          for k,v in my_dict.items():
              if v== True:
                  temp.append(k)
          ambience = temp
    id_dic["ambience"] = ambience
    id_dic["categories"] = categories
    id_dic["reviews"] = [] #initialize reviews as an empty list--these will be put in later
    json_merge[bus_id] = id_dic #add to the merge json

print("after business")

for line in review_file:
  current_json = json.loads(line)
  review_dic = {}
  bus_id = current_json["business_id"]
  #only look at restaurants from json_merge dic
  if bus_id in json_merge and current_json["stars"] >= 3:
    bus_dic = json_merge[bus_id] #dictionary of the current restaurant
    stars = current_json["stars"]
    useful = current_json["useful"]
    text = current_json["text"]
    #add stars, useful, and text part of the review to the review dic
    review_dic["stars"] = stars
    review_dic["useful"] = useful
    review_dic["text"] = text
    #add the new dic to the corresponding "review" list in json_merge
    bus_dic["reviews"].append(review_dic)

print("after review")
json_to_write = {}
for key in json_merge:
  #create the location key from the city/state
  city = json_merge[key]["city"]
  # state = json_merge[key]["state"]
  loc = city.upper()
  #loc.replace(" ","") #remove spaces
  #for example, new york city will have a loc variable of NEWYORKNY

  #the value in the json_to_write dic is  another dic where the keys are the restaurant names
  #and the values are the info/reviews of the restaurants
  name = json_merge[key]["name"]
  #name.replace(" ","")
  name.upper()

  if not loc in json_to_write:
    json_to_write[loc] = {} #initialize entry in json for a new city/state
  info_dic = {} #dic representing info/reviews about the restaurant
  reviews = sorted(json_merge[key]["reviews"],key = lambda i: i['useful'],reverse=True)
  reviews2 = reviews[:2]
  print(len(reviews2))

  ids = json_merge[key]["ID"]
  info_dic["id"] = ids
  price = json_merge[key]["price"]
  info_dic["price"] = price
  categories = json_merge[key]["categories"]
  info_dic["categories"] = categories
  ambience = json_merge[key]["ambience"]
  info_dic["ambience"] = ambience
  #attributes = json_merge[key]["attributes"]
  info_dic["reviews"] = reviews2


  #if dataset still too large: sort the reviews based on "useful" rating and only include the top 10 (?)
  #info_dic["attributes"] = attributes
  #adds restaurant info to the json
  json_to_write[loc][name] = info_dic

print("after merge")
#put new json/dataset into output file
output_file.write(json.dumps(json_to_write)+'\n')