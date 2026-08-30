import sys, os, re
import matplotlib.pyplot as plt

#class segment
class Task:
    def __init__(self, code="0", name="Undefined", tags=None, properties=None):
        self.code = code
        self.name = name
        self.tags = tags if tags else []
        self.properties = properties if properties else {}

    def __str__(self):
        head = [f"#{key}:{val}" for key,val in self.properties.items()]
        tail = " ".join(head+[f"#{i}" for i in self.tags])
        return f"[{self.code}] {self.name} {tail}"

    def GetEstimatedHours(self):
        try:
            return int(self.properties.get("estimatedhours",0))
        except:
            return 0

    def IsUrgent(self):
        return "urgent" in self.tags

    def HasProperty(self, name, value):
        return self.properties.get(name)==value

class Member:
    def __init__(self, name, username):
        self.name=name
        self.username=username
        self.tasks=[]

        def __str__(self):
            text = f"{self.name} <{self.username}>\n"
            if not self.tasks:
                for i in self.tasks:
                    text += " " + str(i) + "\n"
            else:
                text += " (no tasks)\n"
            return text.strip()

    def AddTask(self, task):
        self.tasks.append(task)

    def GetWorkload(self):
        total=0
        for i in self.tasks:
            total+=i.GetEstimatedHours()
        return total

    def GetUrgentTasks(self):
        return [i for i in self.tasks if i.IsUrgent()]

    def GetTasksByProperty(self, prop, val):
        return [i for i in self.tasks if i.HasProperty(prop,val)]

class Manager(Member):
    def __init__(self, name, username):
        super().__init__(name, username)
        self.expertise=set()

    def __str__(self):
        text=f"{self.name} <{self.username}>\n"
        text+="Expertise: "+(", ".join(self.expertise) if self.expertise else "(none)")+"\n"
        for i in self.tasks:
            text+=" "+str(i)+"\n"
        return text.strip()

    def AddTask(self, task):
        self.tasks.append(task)
        for i in task.tags:
            self.expertise.add(i)

class Team:
    def __init__(self, name, code):
        self.name=name
        self.code=code
        self.members=[]

    def AddMember(self, member):
        if member: self.members.append(member)

    def GetWorkload(self):
        total=0
        for i in self.members:
            total+=i.GetWorkload()
        return total

    def GetUrgentTasks(self):
        all=[]
        for i in self.members:
            all+=i.GetUrgentTasks()
        return all

    def GetBusiestMember(self):
        if not self.members: return None
        busiest=max(self.members,key=lambda i:i.GetWorkload())
        return busiest if busiest.GetWorkload()>0 else None

    def GetTasksByProperty(self, prop, val):
        lst=[]
        for i in self.members:
            lst+=i.GetTasksByProperty(prop,val)
        return lst

#data load segment
def LoadData(fileName):
    #I did not test fully regexes so there can be little chance to give false trues etc.
    memberRegex=re.compile(r"^([A-Za-z ]+)\s+<([A-Za-z0-9]+)>$")
    managerRegex=re.compile(r"^([A-Za-z ]+)\s+<!([A-Za-z0-9]+)>$")
    teamRegex=re.compile(r"^([\w ]+)\s*<(\w+)>\s*->\s*([\w,\s]+)$")
    taskRegex=re.compile(r"^\[(\w+)\]\s+(.+?)\s+@(\w+)\s+(#.+)$")

    users={}
    teams={}

    try:
        with open(fileName,"r",encoding="utf-8") as file:
            lines=file.readlines()
    except:
        print("file opening error",fileName)
        return []

    for i in lines:
        i=i.strip()
        if not i or i.startswith("#"): continue

        matchManager=managerRegex.fullmatch(i)
        if matchManager:
            fullName,userName=matchManager.groups()
            users[userName]=Manager(fullName,userName)
            continue

        matchMember=memberRegex.fullmatch(i)
        if matchMember:
            fullName,userName=matchMember.groups()
            users[userName]=Member(fullName,userName)
            continue

        matchTeam=teamRegex.fullmatch(i)
        if matchTeam:
            teamName,teamCode,memberList=matchTeam.groups()
            team=Team(teamName,teamCode)
            for j in [j.strip() for j in memberList.split(",") if j.strip()]:
                if j in users: team.AddMember(users[j])
            teams[teamCode]=team
            continue

        matchTask=taskRegex.fullmatch(i)
        if matchTask:
            taskCode,taskName,assignedUser,tail=matchTask.groups()
            props={}
            tags=[]
            for j in tail.split("#"):
                j=j.strip()
                if not j: continue
                if ":" in j:
                    key,val=j.split(":",1)
                    props[key.strip()]=val.strip()
                else:
                    tags.append(j.strip())
            task=Task(taskCode,taskName,tags,props)
            if assignedUser in users: users[assignedUser].AddTask(task)
            continue

    return list(teams.values())

def PrintManagersByExpertise(teams):
    expertise=input("Enter expertise: ").strip()
    any=False
    processedManagers=set()
    for i in teams:
        for j in i.members:
            if isinstance(j,Manager) and j.username not in processedManagers:
                processedManagers.add(j.username)
                if expertise in j.expertise:
                    print("\n"+str(j))
                    any=True
    if not any:
        print("No managers with",expertise)

def PrintUrgentTasks(teams):
    for i in teams:
        urgentTasks=i.GetUrgentTasks()
        if not urgentTasks:
            print("\nNo urgent tasks for",i.name)
        else:
            print("\nUrgent in",i.name+":")
            for j in urgentTasks:
                print(" ",j)

def PrintTeamWorkloads(teams):
    labels=[]
    values=[]
    for i in teams:
        workload=i.GetWorkload()
        if workload>0:
            labels.append(i.name)
            values.append(workload)
    if not values:
        print("No workload")
        return
    plt.pie(values,labels=labels,autopct="%1.1f%%")
    plt.title("Team Workloads")
    plt.show()

def PrintBusiestMembers(teams):
    for team in teams:
        busiestMember=team.GetBusiestMember()
        if busiestMember:
            print(f"\n{team.name} {busiestMember} Total workload: {busiestMember.GetWorkload()} hours")
        else:
            print(f"\nNo busy members in {team.name}.")

def PrintTasksByProperty(teams):
    propertyName=input("Property name: ").strip()
    propertyValue=input("Value: ").strip()
    for i in teams:
        foundTasks=i.GetTasksByProperty(propertyName,propertyValue)
        if not foundTasks:
            print("\nNo matches in",i.name)
        else:
            print("\nTasks in",i.name)
            for j in foundTasks:
                print(" ",j)

def ShowMenu():
    print("\n       MENU\n ")
    print("1) Managers by Expertise")
    print("2) Urgent Tasks")
    print("3) Team Workloads")
    print("4) Busiest Member")
    print("5) Tasks by Property")
    print("0) Exit")

def Main(argv):
    if len(argv)!=2:
        print("Usage: python taskanalyser.py <datafile>")
        return

    dataFile=argv[1]
    if not os.path.isfile(dataFile):
        print("file not found:",dataFile)
        return

    teams=LoadData(dataFile)
    if not teams:
        print("data load error")
        return

    print("data loaded\n")
    while True:
        ShowMenu()
        choice=input("choice: ").strip()
        if choice=="1": PrintManagersByExpertise(teams)
        elif choice=="2": PrintUrgentTasks(teams)
        elif choice=="3": PrintTeamWorkloads(teams)
        elif choice=="4": PrintBusiestMembers(teams)
        elif choice=="5": PrintTasksByProperty(teams)
        elif choice=="0":
            print("exit")
            break
        else:
            print("invalid option")

if __name__=="__main__":
    Main(sys.argv)
