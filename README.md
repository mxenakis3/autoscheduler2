Installation

* NodeJS:   
  * runtime environment allowing you to run JS code outside of a browser  
  * Widely used for building  
    * Back end applications  
    * Command line tools  
  * Claude likely uses JS/TypeScript and npm packages  
  * Npm: javascript equivalent to pip  
* WSL: Windows Subsystem for Linux  
  * Operating system:   
    * manages computer hardware and software resources  
    * Provides a platform for applications to run on  
  * Ubuntu: Distribution of Linux Kernel, allows you to run Linux Bash on windows, as a sort of application, *alongside* the windows OS  
  * You have a separate file system from windows  
  * To make things not slow, you need to stay on the Linux side– otherwise you will have to deal with constant I/O of moving files from mnt/c:/Users…. To your Linux drive  
* Launching Ubuntu:  
  * Start → ubuntu  
  * To launch vscode:   
    * “code .”  
    * Then you can run Linux commands in the terminal  
* Launching Claude  
  * Run “claude”

Docker:

* Virtualization: Dividing computer resources on separate machines [https://www.youtube.com/watch?v=eyNBf1sqdBQ](https://www.youtube.com/watch?v=eyNBf1sqdBQ)  
  * Web Apps: (mail, databases, music streaming) require centralized servers for database storage. In old times, each application could only be run on one dedicated server. This wasted resources.   
  * Virtual Machine: Instead of hosting one application per server, you can host multiple applications per server by dividing the server’s resources into virtual machines  
    * Hypervisor: software program dividing server/host’s resources among virtual machines  
  * Downsides of VM’s:  
    * Consume a lot of disk space, because each VM has its own dedicated operating system  
    * Slow to start up  
    * Requires a license (?) for the OS  
  * Container: contains only an application, packaged with necessary to run (for each computing environment)  
    * Files  
    * Configurations  
    * Dependencies  
  * A server now has to have hardware resources, its own operating system, and a containerization engine like Docker  
  * Docker has two different types of containers, and thus 2 different types of container engines:  
    * PC  
    * Linux  
  * Almost all Docker containers are Linux based  
  * Whether you run commands from ubuntu shell or powershell, they all get routed to the same Linux kernel (if you are using WSL)  
      
    

Neo4j on Docker:

* IP Address : Hotel; Port: Room  
* You can create a container to run Neo4j on your laptop for your local machine to run as the server  
* Docker containers are built for specific OS kernels  
  * Windows  
  * Linux  
* Useful commands:  
  * Docker Ps: process status – see what processes are going on under the hood  
  * Docker start \<name\>: starts a container