

shoes = ['Air Skylon 2 Fear of God White', 'Air Skylon 2 Fear of God Black Sail', 'Nike SB Dunk Low Concepts Green Lobster (Special Box)', 'Kyrie 5 Concepts Ikhet', 'Air Force 1 Low A Cold Wall White', 'Nike SB Dunk Low Doernbecher (2018)', 'Air Max 97 Silver White', 'Kyrie 5 Taco PE', 'Nike PG 2.5 Playstation Multi-Color']

def search_terms(string):
    relevanceList = []
    for shoe in shoes:
        ignoreList = [ 'of', 'a', 'the' ]
        searchTerms = string.lower().split(' ')
        searchFor = shoe.lower().split(' ')
        x = 0
        for terms in searchTerms:
            if terms in ignoreList:
                pass
            elif terms in searchFor:
                    x += 1
            else:
                pass
        
        relevanceList.append((shoe,x))
    relevanceList = sorted(relevanceList, key=lambda x:x[1])[::-1]
    relevanceList = [relevant[0] for relevant in relevanceList]
        
    return relevanceList



print(search_terms('Kyrie concepts'))


        