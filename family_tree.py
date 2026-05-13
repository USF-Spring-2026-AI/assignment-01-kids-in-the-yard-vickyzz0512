import pandas as pd
import random
from collections import deque


class Person:
    
    def __init__(self, first_name, last_name, gender, year_born, year_died):
        self._first_name = first_name
        self._last_name = last_name
        self._gender = gender
        self._year_born = year_born
        self._year_died = year_died
        self._partner = None
        self._children = []
        
    # Accessors
    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name
        
    def get_full_name(self):
        return f"{self._first_name} {self._last_name}"

    def get_year_born(self):
        return self._year_born

    def get_year_died(self):
        return self._year_died
        
    def get_gender(self):
        return self._gender  
    
    def get_partner(self):
        return self._partner
     
    def get_children(self):
        return self._children

    # Mutators
    def set_partner(self, partner):
        self._partner = partner

    def add_child(self, child):
        self._children.append(child)    
        
        
class PersonFactory:
    
    def __init__(self):
        self._life_expectancy = {}       
        self._first_names_by_prob = {}           
        self._last_names_by_rank = {}  
        self._gender_name_prob = {} 
        self._rank_to_prob = {}          
        self._birth_marriage = {} 
        

    def read_files(self): 
        self.read_rank_to_prob()
        self.read_life_expectancy()
        self.read_first_names_by_prob()
        self.read_last_names_by_rank()
        self.read_gender_name_prob()
        self.read_birth_marriage()
        
        
    # life expenctancy
    def read_life_expectancy(self):
        self.df_life_expectancy = pd.read_csv("life_expectancy.csv")
        for _, row in self.df_life_expectancy.iterrows():
            year = int(row["Year"])
            self._life_expectancy[year] = float(
                row["Period life expectancy at birth"]
            )
            
    # first name       
    def read_first_names_by_prob(self):
        self.df_first_names_by_prob = pd.read_csv("first_names.csv")
        
        for _, row in self.df_first_names_by_prob.iterrows():
            decade = row["decade"]
            gender = row["gender"]
            name = row["name"]
            frequency = float(row["frequency"])
            if decade not in self._first_names_by_prob:
                self._first_names_by_prob[decade] = {gender: ([], [])} # {decade: {gender: ([name list], [freq list])}}
            if gender not in self._first_names_by_prob[decade]:
                self._first_names_by_prob[decade][gender] = ([], [])
            self._first_names_by_prob[decade][gender][0].append(name)
            self._first_names_by_prob[decade][gender][1].append(frequency)

    # last name
    def read_last_names_by_rank(self):
        self.df_last_names_by_rank = pd.read_csv("last_names.csv")

        for _, row in self.df_last_names_by_rank.iterrows():
            decade = row["Decade"]
            rank = row["Rank"]
            name = row["LastName"]
            frequency = self._rank_to_prob[rank]
            if decade not in self._last_names_by_rank:
                self._last_names_by_rank[decade] = ([], []) # {decade: ([name list], [freq list])}
            self._last_names_by_rank[decade][0].append(name)
            self._last_names_by_rank[decade][1].append(frequency)

    # gender name probability
    def read_gender_name_prob(self):
        self.df_gender_name_prob = pd.read_csv("gender_name_probability.csv")
        
        for _, row in self.df_gender_name_prob.iterrows():
            decade = row["decade"]
            gender = row["gender"]
            frequency = row["probability"]
            if decade not in self._gender_name_prob:
                self._gender_name_prob[decade] = ([], []) # {decade: ([gender list], [freq list])}
            self._gender_name_prob[decade][0].append(gender)
            self._gender_name_prob[decade][1].append(frequency)

    # rank to probability
    def read_rank_to_prob(self):
        self.df_rank_to_prob = pd.read_csv("rank_to_probability.csv", header=None)
        self._rank_to_prob = {
            rank: float(prob) 
            for rank, prob in enumerate(self.df_rank_to_prob.T.iloc[:,0], start=1)
        }

    # brith and marriage rates
    def read_birth_marriage(self):
        self.df_birth_marriage = pd.read_csv("birth_and_marriage_rates.csv")
        for _, row in self.df_birth_marriage.iterrows():
            decade = row["decade"]
            self._birth_marriage[decade] = {
                "birth_rate": float(row["birth_rate"]),
                "marriage_rate": float(row["marriage_rate"]),
            }

    def _generate_gender(self, year_born):
        target = (year_born // 10) * 10
        if target > 2120:
            target = 2120
        if target < 1950:
            target = 1950        
        decade = f"{target}s"
        gender_list, freq_list = self._gender_name_prob[decade]
        return self._select_by_probability(gender_list, freq_list)

    def _select_by_probability(self, value_list, prob_list):
        cum_prob_list = [0]
        for prob in prob_list:
            cum_prob_list.append(cum_prob_list[-1] + float(prob))

        random_prob = random.random()
        cum_prob_list = [cum_prob / cum_prob_list[-1] for cum_prob in cum_prob_list]
        element_index = [cum_prob > random_prob for cum_prob in cum_prob_list].index(True) - 1
        return value_list[element_index]
        
    def _generate_first_name(self, year_born, gender):
        target = (year_born // 10) * 10
        if target > 2120:
            target = 2120
        if target < 1950:
            target = 1950     
        decade = f"{target}s"
        name_list, freq_list = self._first_names_by_prob[decade][gender]
        return self._select_by_probability(name_list, freq_list)

    def _generate_last_name(self, year_born):
        target = (year_born // 10) * 10
        if target > 2120:
            target = 2120
        if target < 1950:
            target = 1950     
        decade = f"{target}s"
        name_list, freq_list = self._last_names_by_rank[decade]
        return self._select_by_probability(name_list, freq_list)

    def _generate_year_died(self, year_born):
        if year_born < 1950:
            year_born = 1950
        if year_born > 2120:
            year_born = 2120

        life_expectancy = self._life_expectancy[year_born]
        life_variation = random.random() * 20 - 10
        year_died = int(year_born + life_expectancy + life_variation)
        return year_died
    
    # getperson
    def get_person(self, year_born, first_name=None, last_name=None, gender=None):
        if gender is None:
            gender = self._generate_gender(year_born)
        if first_name is None:
            first_name = self._generate_first_name(year_born, gender)
        if last_name is None:
            last_name = self._generate_last_name(year_born)
        year_died = self._generate_year_died(year_born)
        return Person(
            first_name=first_name,
            last_name=last_name,
            year_born=year_born,
            year_died=year_died,
            gender=gender
        )


class FamilyTree:
    
    def __init__(self):
        self._max_year = 2120
        self._founder1 = None
        self._founder2 = None
        self._family_members = []
        self._factory = PersonFactory()
        self._factory.read_files()
    
    def set_founder1(self):
        self._founder1 = self._factory.get_person(
            first_name="Desmond",
            last_name="Jones",
            year_born=1950,
            gender="male"
        )
        self._family_members.append(self._founder1)

    def set_founder2(self):
        self._founder2 = self._factory.get_person(
            first_name="Molly",
            last_name="Jones",
            year_born=1950,
            gender="female"
        )
        self._family_members.append(self._founder2)

    def get_decade(self, year_born):
        target = (year_born // 10) * 10
        if target > 2120:
            target = 2120
        if target < 1950:
            target = 1950     
        decade = f"{target}s"
        return decade

    def generate_partner(self, year_born, gender):
        decade = self.get_decade(year_born)
        marriage_rate = self._factory._birth_marriage[decade]["marriage_rate"]
        if random.random() < marriage_rate: # generate a partner
            partner_year_born = year_born + random.randint(-10,10)
            partner_gender = "female" if gender == "male" else "male"
            return self._factory.get_person(
                year_born=partner_year_born,
                gender=partner_gender
            )
        return None

    def generate_children(self, year_born, has_partner=True, inherited_last_name=None): # if partners year born is different, then we need to pick one from two partners to determine their number of chidren. we select year_born from elder parent to determine their children number
        decade = self.get_decade(year_born)
        birth_rate = self._factory._birth_marriage[decade]["birth_rate"]
        num_children = random.randint(
            int(birth_rate - 1.5),
            int(birth_rate + 1.5)
        )
        
        # a person who does not have a partner or spouse will have 1 child fewer than a person who has a partner or spouse.
        if not has_partner:
            num_children -= 1

        num_children = max(num_children, 0)    
        earliest = year_born + 25
        latest = year_born + 45 
        if num_children > 1:
            step = (latest - earliest) / (num_children - 1)
            child_years = [round(earliest + i * step) for i in range(num_children)]
        elif num_children == 1:
            child_years = [random.randint(earliest, latest)]
        else:
            child_years = []


        children_list = []
        for child_year_born in child_years:
            children_list.append(
                self._factory.get_person(
                    year_born=child_year_born,
                    last_name=inherited_last_name
                )
            )
        
        return children_list
    
    def generate(self,):
        if self._founder1 is None:
            self.set_founder1()
        if self._founder2 is None:
            self.set_founder2()

        self._founder1.set_partner(self._founder2)
        self._founder2.set_partner(self._founder1)            

        queue = deque([[self._founder1, self._founder2]])
        inherited_names = {id(self._founder1): "Jones", id(self._founder2): "Jones"}

        while queue:
            partners = queue.popleft()
            has_partner = len(partners) > 1
            elder_partner_year_born = max([p.get_year_born() for p in partners])

            parent_inherited = next(
                (inherited_names.get(id(p)) for p in partners if id(p) in inherited_names),
                None,
            )

            children = self.generate_children(elder_partner_year_born, has_partner, inherited_last_name=parent_inherited,)
            
            for child in children:
                if child.get_year_born() > self._max_year:
                    continue
                
                for partner in partners:
                    partner.add_child(child)
                
                self._family_members.append(child)

                if parent_inherited is not None:
                    inherited_names[id(child)] = parent_inherited
            
                child_partner = self.generate_partner(child.get_year_born(), child.get_gender())
                if child_partner:
                    if child_partner.get_year_born() > self._max_year:
                        queue.append([child])
                    else:    
                        self._family_members.append(child_partner)
                        child.set_partner(child_partner)
                        child_partner.set_partner(child)
                        queue.append([child, child_partner])
                else:
                    queue.append([child])
                
    def get_total_people_number(self):
        return len(self._family_members)
        
    def get_total_people_number_by_year(self):
        decade_counts = {}

        for person in self._family_members:
            decade_start = (person.get_year_born() // 10) * 10
            decade_counts[decade_start] = decade_counts.get(decade_start, 0) + 1
        return dict(sorted(decade_counts.items()))
    
    def get_duplicate_names(self):
        family_members_full_name = [person.get_full_name() for person in self._family_members]
        names_count = pd.Series(family_members_full_name).value_counts().to_dict()
        duplicated_names = []
        for name, name_count in names_count.items():
            if name_count > 1:
                duplicated_names.append(name)
        return duplicated_names

    def run(self):
        # generate family tree
        self.generate()
        
        menu = (
            "\nAre you interested in:\n"
            "(T)otal number of people in the tree\n"
            "Total number of people in the tree by (Y)ear\n"
            "(N)ames duplicated\n"
            "(Q)uit\n"
        )
        while True:
            print(menu)
            raw = input("> ").strip()
            if not raw:
                continue
            choice = raw[0].upper()

            if choice == "T":
                print(f"\nThe tree contains {self.get_total_people_number()} people total")

            elif choice == "Y":
                print()
                for year, count in self.get_total_people_number_by_year().items():
                    print(f"{year}: {count}")

            elif choice == "N":
                dupes = self.get_duplicate_names()
                print()
                if dupes:
                    print(
                        f"There are {len(dupes)} duplicate names in the tree:"
                    )
                    for name in dupes:
                        print(f"  * {name}")
                else:
                    print("There are no duplicate names in the tree.")

            elif choice == "Q":
                print("Goodbye!")
                break

            else:
                print("Invalid choice — please enter T, D, N, or Q.")
    

if __name__=="__main__":
    family_tree = FamilyTree()
    family_tree.run()
    