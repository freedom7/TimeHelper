# -*- coding:utf-8 -*-
from account.models import Account,UserGroup

class TimeData(object):
    count = None
    start_time = None
    end_time = None
    userlist = None

    def __init__(self,start_time,end_time,userlist,count=1):
        self.count = count
        self.start_time = start_time
        self.end_time = end_time
        self.userlist = userlist

    def add(self,user):
        self.count += 1
        self.userlist.append(user)

    def clone(self):
        td = TimeData(self.start_time,self.end_time,self.userlist[:],self.count)
        return td

    def __repr__(self):
        return '%s--%s %d'%(self.start_time,self.end_time,self.count)
    def __str__(self):
        return '%s-%s'%(self.start_time,self.end_time)
    def __eq__(self,obj):
        return self.start_time == obj.start_time and self.end_time == obj.end_time

def approach_time(time):
    minute = ((time.minute + 5)/10)*10
    return time.replace(minute=minute,second=0)

def approach_time_list(time_list):
    for time in time_list:
        time.start_time = approach_time(time.start_time)
        time.end_time = approach_time(time.end_time)
    return time_list

def getGroupTimeDetails(user,group):
    #Get all member's timedetail in a group by user
    members = group.member.all()
    time_user_list = []
    for member in members:
        group_time_list = member.timedetail_useto.filter(useto=user,free=True)
        time_user_list.append(group_time_list)
    return time_user_list

def timeToPerson(timedata,weekday=None):
    #Get userlist between timedata.start_time and timedata.end_time
    
    timedata.start_time = approach_time(timedata.start_time)
    timedata.end_time = approach_time(timedata.end_time)
    
    user = timedata.userlist[0]
    groups = UserGroup.objects.filter(member=user)
    group_time_list = []
    for group in groups:
        if weekday:
            time_list = group.user.timedetail_user.filter(useto=user,free=True,weekday=weekday)
        else :
            time_list = group.user.timedetail_user.filter(useto=user,free=True)
        group_time_list.append(time_list)
    person_list = []
    for member_list in group_time_list:
        for item in member_list:
            item.start_time = approach_time(item.start_time)
            item.end_time = approach_time(item.end_time)
            if timedata.start_time<=item.start_time<timedata.end_time \
            or timedata.start_time<item.end_time<=timedata.end_time \
            or (timedata.start_time>=item.start_time and timedata.end_time<=item.end_time) :
                person_list.append(item)
    return person_list

def getSingleTimeDetails(user, member):
    single_time_list = member.usergroup_user.filter(member=user,free=True)
    return single_time_list

def getSingleFreeTime(user, person):
    time_list = person.timedetail_user.filter(useto=user,free=True)
    return time_list

def getMemberTimeList(user, member, group_tmp):
    member_time_list = list(member.timedetail_user.filter(useto=user,free=True))
    member_group = member.usergroup_user.filter(member=user)
    for group in member_group:
        #去重分组
        if group in group_tmp:
            continue
        else :
            group_tmp.append(group)
        group_time_list = member.timedetail_user.filter(useto_group=group,free=True)
        member_time_list.extend(group_time_list)
    tmp = {}
    #去重时间段
    for time in member_time_list:
        tmp[time.id] = time
    member_time_list = tmp.values()
    return member_time_list

def reGroupByWeek(time_list):
    user_weekday = []
    for i in range(1,8):
        user_weekday.append(filter(lambda x:x.weekday==str(i),time_list))
    # user_weekday_1 = filter(lambda x:x.weekday==u'1',time_list)
    # user_weekday_2 = filter(lambda x:x.weekday==u'2',time_list)
    # user_weekday_3 = filter(lambda x:x.weekday==u'3',time_list)
    # user_weekday_4 = filter(lambda x:x.weekday==u'4',time_list)
    # user_weekday_5 = filter(lambda x:x.weekday==u'5',time_list)
    # user_weekday_6 = filter(lambda x:x.weekday==u'6',time_list)
    # user_weekday_7 = filter(lambda x:x.weekday==u'7',time_list)
    # user_weekday = [user_weekday_1,user_weekday_2,user_weekday_3,user_weekday_4,user_weekday_5,user_weekday_6,user_weekday_7]
    return user_weekday

def get_oneDay_freeTime_data(all_oneDays,user_oneDays,user,exact=False):
    # Sort by Great > Bellow
    all_oneDays = sorted(all_oneDays,cmp=lambda u_x,u_y:cmp(u_y.start_time,u_x.start_time))
    if not exact:user_oneDays = approach_time_list(user_oneDays)
    user_oneDays = sorted(user_oneDays,cmp=lambda u_x,u_y:cmp(u_y.start_time,u_x.start_time))
    new_all_oneDays = all_oneDays[:]

    while all_oneDays or user_oneDays:
        if all_oneDays:
            all_oneDay=all_oneDays.pop()
        else:
            all_oneDay = None
        if user_oneDays:
            user_oneDay=user_oneDays.pop()
        else:
            user_oneDay = None

        if all_oneDay and not user_oneDay:
            pass
        elif user_oneDay and not all_oneDay:
            td = TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,])
            new_all_oneDays.append(td)
        else:
            if all_oneDay.start_time == user_oneDay.start_time:
                if all_oneDay.end_time == user_oneDay.end_time:
                    index = new_all_oneDays.index(all_oneDay)
                    new_all_oneDays[index].add(user)
                elif all_oneDay.end_time < user_oneDay.end_time:
                    tdmid = all_oneDay.clone()
                    index = new_all_oneDays.index(tdmid)
                    tdmid.add(user)
                    new_all_oneDays[index] = tdmid
                else :
                    tdmid = all_oneDay.clone()
                    tdmid.end_time = user_oneDay.end_time
                    tdmid.add(user)
                    new_all_oneDays.append(tdmid)
            elif all_oneDay.start_time < user_oneDay.start_time:
                if all_oneDay.end_time <= user_oneDay.start_time:
                    user_oneDays.append(user_oneDay)
                elif all_oneDay.end_time > user_oneDay.start_time:
                    if all_oneDay.end_time < user_oneDay.end_time:
                        tdmid = all_oneDay.clone()
                        tdmid.add(user)
                        tdmid.start_time = user_oneDay.start_time
                        new_all_oneDays.append(tdmid)
                        tdnext = TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,])
                        new_all_oneDays.append(tdnext)
                    else:
                        tdmid = all_oneDay.clone()
                        tdmid.start_time = user_oneDay.start_time
                        tdmid.end_time=user_oneDay.end_time
                        tdmid.add(user)
                        new_all_oneDays.append(tdmid)
            else :
                if user_oneDay.end_time <= all_oneDay.start_time:
                    new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
                    all_oneDays.append(all_oneDay)
                else :
                    if user_oneDay.end_time < all_oneDay.end_time:
                        new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
                        tdmid = all_oneDay.clone()
                        tdmid.end_time=user_oneDay.end_time
                        new_all_oneDays.append(tdmid)

                    else :
                        tdmid = all_oneDay.clone()
                        index = new_all_oneDays.index(tdmid)
                        tdmid.add(user)
                        new_all_oneDays[index] = tdmid
                        new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
    return new_all_oneDays

def get_oneWeek_freeTime_Data(all_oneWeeks,user_oneWeeks,user):
    new_all_oneWeeks = []
    for index in range(7):
        new_all_oneWeeks.append(get_oneDay_freeTime_data(all_oneWeeks[index],user_oneWeeks[index],user))
    return new_all_oneWeeks

def get_Somebody_freeTime_Data(user,memberlist):
    #user = Account.objects.get(user=user)    
    try :
        time_list = user.timedetail_user.all()
        user_weekdays = reGroupByWeek(time_list)
        weekday_data= [[],[],[],[],[],[],[]]
        user_weekday_data = get_oneWeek_freeTime_Data(weekday_data,user_weekdays,user)
        
        new_weekday_data = user_weekday_data
        group_tmp = []
        for member in memberlist:
            member_time_list = getMemberTimeList(user,member,group_tmp)
            # member_time_list = member.timedetail_user.filter(useto=user,free=True)
            member_weekdays = reGroupByWeek(member_time_list)
            new_weekday_data = get_oneWeek_freeTime_Data(new_weekday_data,member_weekdays,member)
        return new_weekday_data
    except Account.DoesNotExist:
        pass


def get_userGroup_freeTime_Data(user,group_name):
    #user = Account.objects.get(user=user)    
    try :
        user_group = UserGroup.objects.get(user=user,group_name=group_name)
        time_list = user.timedetail_user.all()
        user_weekdays = reGroupByWeek(time_list)
        weekday_data = [[],[],[],[],[],[],[]]
        user_weekday_data = get_oneWeek_freeTime_Data(weekday_data,user_weekdays,user)
        
        new_weekday_data = user_weekday_data
        group_tmp = []
        for member in user_group.member.all():
            member_time_list = getMemberTimeList(user,member,group_tmp)
            member_weekdays = reGroupByWeek(member_time_list)
            new_weekday_data = get_oneWeek_freeTime_Data(new_weekday_data,member_weekdays,member)
        return new_weekday_data
    except Account.DoesNotExist:
        pass

