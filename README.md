Autoscheduler: Program that uses LLM agents to help project management scheduling (ie.CPM). Program uses LLM agents to generate/remove project scope on behalf of the user. Vector DB used to query the schedule for activities pertaining to user prompts (ie. get me all activities on the first floor)

Context and Background:

* Representing Activities and Relationships in the Schedule:  
* Activity Representation (High Level):  
  * An activity consists of a start node, an end node, and an intra-activity node  (description to follow) representing the duration of the node.   
  * There is a directed edge from S→intra, intra→E, with 0 weight  
  * NOTE: When calculating critical path, the duration is picked up by intra  
  * Activity class implemented in Pydantic  
    * ActivitySchema:  
      * Activity\_id: UUID  
        * Name: str  
        * Description: str  
        * Duration: str  
* Relationship (High Level): A separate node representing a relationship between start, end type nodes by a directed edge from a predecessor to successor node.    
  * Ex: SS relationships represented as directed edge from S\_1 to S\_2.   
  * As mentioned, an activity is represented with a relationship node between its start and finish  
  * Properties of a relationship node:  
    * RelationshipSchema:  
      *     id: UUID \= Field(default\_factory=uuid4)  
        *     type: RelationshipType  
        *     predecessor: ActivitySchema  
        *     successor: ActivitySchema  
        *     Lag: str= Field(default=0, description="Lag time in days")  
        *     class Config:  
        *         json\_encoders \=UUID: str }  
      * RelationshipType(str, Enum): Supported relationship types in project scheduling  
        *     FS \= "FS" : Finish-to-Start  
        *     SS \= "SS" :  Start-to-Start  
        *     FF \= "FF" : Finish-to-Finish  
        *     SF \= "SF" : Start-to-Finish  
  * Two different databases will be used to represent the entire schedule:  
    * Neo4J graph database: Stores network topology, including the sub-nodes of each Activity (description of Activity to follow in schedule section)  
    * Vector Database: OpenAI Embeddings, stores only Activity and Inter-Activity relationship nodes  
* Context, Clarifications & Summary of Node & Relationship Types:  
  * Databases get uniqueness guarantees on ID through UUIDs for now  
  * Intra-activity nodes use relationship class to finish initializing the activity  
  * Inter-activity nodes use relationship class to set up FS, SS, FF relationships  
  * Inter-activity nodes are added to the Vector DB  
  * Activity nodes are added to the Vector DB, but its sub-nodes are lower level logic that do not take part in the semantic search   
  * All nodes are added to the Neo4j database, with nondescript edges  
  * Vector database is queried by semantic search, and when the results arrive, logic is executed within the activity sub nodes (to avoid problem of destructive changes due to an incomplete semantic search missing start/ends, for example)

Schedule Class: Contains the database and NetworkX representation of the schedule

* Attributes:  
  * Neo4j Database: Simply used to store the schedule logic and supply NetworkX with the graph topology so that it can create renderings of the schedule in progress. For now, it is not used at all in similarity search.  
    * Table: Nodes:  
      * Id: Unique node identifier. The high-level activity nodes are NOT in this database. ONLY the lower-level nodes, including:  
        *  the “s-” or “e-” prepended identifier for the ‘subnode’ representing the start/end of an activity  
        * The unique relationship ID for a relationship node  
      * Duration: The ‘weight’ of the node  
        * 0 if it is a “s-” or “e-” node. (The s/e nodes simply function as endpoints for the activities)  
        * If a relationship node, then this is a string value representing the duration of the node (could be an integer value, or a numpy distribution, for example)  
          * If intra-activity, duration represents an activity duration  
          * If inter-activity, this represents lag  
    * Table: Edges:  
      * We only use one edge type for now: “precedes”. This is used to create directed edges from start to end nodes  
  * NetworkX DiGraph:  Lightweight graph representation loaded from Neo4j database. Can be used to compute critical paths  
    * Recomputed when self.schedule (below) called  
  * Embeddings Matrix: Nodes for Activities and inter-activity relationships   
    * There will be two databases, one for activities and another for relationships  
    * Activities:  
    * Schema :

      { "id": "uuid",

       "name": "string",

       "description": "string",

       "duration": "int | distribution",

      "start\_node": "neo4j\_id",

      "end\_node": "neo4j\_id",}

    * Fields  
      * ID: Unique identifier of high-level activity (distinct from subnode ids) (not in embedding)  
      * Start: contains pointer to start node in Neo4j database (not in embedding)  
      * End: contains pointer to end node in Neo4j database (not in embedding)  
      * Name: Activity name (in embedding)  
      * Duration: Activity duration (in embedding)  
      * Description: Activity description (in embedding)   
      * Validated in Pydantic Class ActivitySchema()  
    * Relationships:  
      * Schema: { "id": "uuid", "type": "FS | SS | FF | SF", "predecessor": {  "activity\_id": "uuid", “name”: “string” "description": "string", "duration": "int”}, "successor": { "activity\_id": "uuid", “name”: “string” "description": "string", "duration": "int"}, "lag": "int"}  
      * Fields:  
        * ID: Unique relationship ID  
        * Predecessor information: (Could key into Activities DB).  
          * Activity ID of predecessor  
          * Name (in embedding)  
          * Description (in embedding)  
          * Duration (in embedding)  
        * Successor information (Could key into Activities DB).  
          * Activity ID of predecessor  
          * Name (in embedding)  
          * Description (in embedding)  
          * Duration (in embedding)  
      * Validated in pydantic class RelationshipFormat()

Scope Manager Class: Interface between CLI and schedule. Parses user requests into scope changes, which then get implemented in schedule. 

* Methods:  
  * \_dispatch: Entry point for open ended user prompts  
    * Inputs:   
      * None  
    * Outputs:  
      * bool: True if user accepts changes, False if user rejects or cancels  
    * Function:  
      * Cache the current schedule  
        * If user cancels or exits, schedule should be restored to this state  
        * As changes to the schedules are being suggested, the schedule will be modified in place, so the cache is important for preserving the record  
      * Initialize a buffer memory  
        * Will be used to track the scope changes the LLM makes to the schedule  
      * Prompt user:   
        * “Enter a command for the schedule. Examples:”   
          * “Add activities for excavation on floor 1”  
          * “Delete all activities on the second floor”  
      * Call \_separate\_prompt(user\_input) to separate prompt into scope additions and scope removals  
      * Call \_read\_scope with toolkit (removals) on removal\_prompt to create a function call for one of the following:  
        * \_delete\_activity: If prompt specifies to delete EXACTLY 1 activity  
        * \_dissolve\_activity: If prompt specifies to dissolve EXACTLY 1 activity  
        * \_delete\_relationship: If prompt specifies to delete EXACTLY 1 relationship  
        * \_remove\_scope: Generic function for removing scope  
        * \_finish: Call if there are no removals to make  
      * Call the function output by \_read\_scope  
      * Call \_read\_scope with toolkit additions to create a function call for one of the following:  
        * \_add\_activity: If prompt asks to add exactly 1 activity  
        * \_add\_relationship: If prompt asks to add exactly 1 relationship  
        * \_add\_scope: If prompt wants us to add more scope in general, but not exactly 1 activity/relationship  
        * Finish: If there are no additions to make  
      * See if user likes the changes:  
        * Present buffer memory of function calls to user  
        * Ask user to accept or reject suggestions  
        * If reject, then ask for feedback  
        * Repeat process (call \_remove\_scope, \_add\_scope) with new user context  
        * Otherwise done  
  * \_separate\_prompt: Separate an unmodified user prompt into scope additions/removals  
    * Inputs:  
      * Prompt (required): Raw user prompt describing desired schedule scope modifications  
    * Outputs:  
      * Additions\_prompt: Derived prompt describing scope additions that need to take place  
      * Removals\_prompt: Derived prompt describing scope removals that must take place  
    * Access via:   
      * \_dispatch  
    * Function:  
      * Use AsyncOpenAI client (regular chat functionality) to separate a user's prompt into two distinct prompts, for scope additions and removals, respectively.   
      * Examples:  
        * User prompt: “Make fitouts on floor 4 come after fitouts on floor 2 instead of floor 3”  
          * Removal prompt: “Delete relationships between fitouts on floor 3 and floor 4”  
          * Additions prompt: “Add missing relationships to ensure that interior fitouts on floor 4 follow interior fitouts on floor 2”  
        * User Prompt: “Delete activity \<uuid\>”  
          * Removal prompt: “Delete activity \<uuid\>”  
          * Additions prompt: None  
  * \_read\_scope: Creates a function call based on a user prompt and a set of tools  
    * Inputs:   
      * Prompt: Derived prompt representing either removal/additions  
      * Toolkit: LLM agent tools available  
    * Returns:  
      * Function call: a function call to make to process the activities  
    * Accessed via:   
      * \_dispatch  
    * Function:  
      * Use AsyncOpenAI tool calling agent with tool-kit (from LLM client class) to parse the scope prompt into the most fitting function call.   
      * Designed to be used for both removal/additions of scope   
  * \_remove\_scope: Main loop handling scope removals:  
    * Inputs:  
      * Removal\_prompt: Derived prompt describing removals that need to take place  
    * Outputs:  
      * bool: True if all removals successful, False if any failed  
    * Access via:  
      * \_dispatch  
    * Function:  
      * Process relationship removals  
        * Use semantic search to identify inter-activity nodes that pertain to removal prompt  
        * For each node identified:  
          * Use LLM to decide whether the relationship-node should be removed  
          * Create a function call (\_delete\_relationship(\*\*params) as a string  
          * Add the string to the buffer memory  
          * Safely call the function to update db  
      * Process activity removals  
        * Use semantic search to identify high-level activity nodes that pertain to removal prompt  
        * For each node identified:  
          * Use LLM to decide whether the activity-node should be removed  
          * Create a function call (\_delete\_activity(\*\*params) as a string  
          * Add the string to the buffer memory  
          * Safely call the function to update db  
  * \_add\_scope: Adds new scope to the schedule based on an open-ended user prompt  
    * Inputs:  
      * Additions\_prompt: Derived prompt representing additions to scope to make  
    * Outputs:  
      * bool: True if all additions successful, False if any failed  
    * Accessed via:  
      * \_dispatch  
    * Function:  
      * Add activities to the schedule based on the prompt  
        * Use LLM-prompt function to output JSON file with the following schema: {‘activity\_name’: \<\>, ‘description’:\<\>, ‘duration’: \<\> }  
        * For each activity:  
          * Give uuid  
          * Parse into ActivitySchema  
          * Pass to \_add\_activity  
          * Add function call \_add\_activity(\<ActivitySchema\>) to buffer memory  
      * Add relationships to the schedule:  
        * Use embeddings DB to query (via semantic search) the activities that might be reasonable to make links between given the prompt  
        * Use LLM to propose changes IN NATURAL LANGUAGE as a jason   
          * Output schema: {‘relationship1’ : Add a start start relationship from mix ingredients to preheat oven, ‘relationship2’: add a finish start relationship from mix ingredients to pour in baking tray’}.  etc.  
        * Use vector DB to pick the most likely (pred, succ) activities in each item  
        * Use OpenAI ‘parse’, and parse each activity into a Pydantic activity class and each relationship type into ‘FF’, ‘FS’ or ‘SS’  
        * Format into a function call to \_add\_relationship  
        * Add function call to buffer memory  
        * Call \_add\_relationship(\<RelationshipFormat\>)  
  * \_add\_activity: Adds a new activity to the Schedule  
    * Inputs:  
      * Prompt (optional): string   
      * Activity() (optional): ActivitySchema  
    * Outputs:   
      * bool: True if activity successfully added, False if failed  
    * Accessed via:  
      * CLI (user chooses add activity option from CLI)  
      * Dispatch:  
        * User prompts LLM  
        * LLM interprets prompt as a call to \_add\_activity (ie. “Add a new activity to the schedule for baking a cake”)  
    * Function:  
      * If ActivitySchema is specified, unpack fields  
      * If prompt is specified, use LLM client to parse into ActivityTemplate for fields:  
        * Name  
        * Description  
        * duration  
      * For remaining unspecified ActivitySchema fields, ask user to provide information  
      * Assign a unique activity\_id (UUID) to activity  
      * Add activity entry to both Neo4j and Embeddings   
        * Include the start, end, and intra relationship nodes in Neo4j  
        * Include the standard activity details for embeddings matrix  
      * Databases  
        * Use two phase commit (try/except logic adding both, and don’t add if both don't work)  
  * \_add\_relationship: Adds a new relationship to the schedule  
    * Inputs:  
      * Prompt (optional)  
      * RelationshipFormat() (optional)  
    * Outputs:  
      * bool: True if relationship successfully added, False if failed  
    * Accessed via:  
      * CLI (user chooses add relationship option from CLI)  
      * Dispatch:  
        * User prompts LLM  
        * LLM interprets prompt as a call to \_add\_relationship (ie. “Add a FS relationship from mix ingredients to pour tray”)  
    * Function: Adds a new activity to the schedule  
      * See relationship schema above for attributes  
      * If RelationshipFormat, harvest for attributes.  
      * If Prompt, harvest for attributes  
      * If any required attributes missing at this point, ask user to fill missing  
      * Add entry to both Neo4j and Embeddings  
        * Inter-activity node added to both Neo4j and Embeddings matrix  
        * Use two phase commit (try/except logic adding both, and don’t add if both don't work)  
  * \_delete\_activity:  
    * Inputs:  
      * Prompt (optional): string   
      * activity\_id (optional): uuid  
    * Outputs:  
      * bool: True if activity successfully deleted, False if not found or failed  
    * Accessed via:  
      * CLI  
      * Dispatch:  
        * User prompts LLM  
        * LLM interprets prompt as a call to \_delete\_activity (ie. “Delete pour tray”)  
    * Function: Deletes a schedule activity  
      * If uuid, find an delete all nodes and edges containing the id as an entry  
      * If prompt, use semantic search to find best match activity and delete activity  
        * Use two phase commit (try/except logic removing both, and don’t add if both don't work)  
  * \_dissolve\_activity  
    * Inputs:  
      * Prompt (optional): string   
      * activity\_id (optional): uuid  
    * Outputs:  
      * bool: True if activity successfully dissolved, False if not found or failed  
    * Accessed via:  
      * CLI  
      * Dispatch:  
        * User prompts LLM  
        * LLM interprets prompt as a call to \_dissolve\_activity (ie. “Dissolve pour tray”)  
    * Function:  
      * Deletes an activity from the schedule, and reattaches all predecessor relationships to successors.  
        * Ex. Activity A has predecessors B, C, D, and successor E. After dissolving, activities B, C, D also have successor E (for any relationship type, preserving lag (the lag from A to E is preserved when B becomes the predecessor to E)  
      * If activity\_id, dissolve that activity  
      * If prompt, use semantic search to find that activity, then dissolve  
      * Else ask user which to dissolve  
  * \_delete\_relationship:  
    * Inputs:  
      * Prompt (optional): string   
      * RelationshipFormat() (optional): uuid  
    * Outputs:  
      * bool: True if relationship successfully deleted, False if not found or failed  
    * Accessed via:  
      * CLI  
      * Dispatch:  
        * User prompts LLM  
        * LLM interprets prompt as a call to \_delete\_activity (ie. “Delete FS relationship between mix ingredients and pour tray”)  
      * Function:   
        * If relationship format, get UUIDs of both activity and rel\_type and delete node representing link in Neo4j database if found  
        * If prompt, find the best matching relationship, return from database in a readable format, allow user to confirm, then delete from database  
        * If neither prompt nor relationship format, ask user to specify the UUIDs and rel type for relationship in question and delete  
  * Schedule: Basically commits changes the user has enqueued to the schedule, refreshes the database, and updates the Networkx digraph  
    * Compiles a NetworkX digraph from the Neo4j graph database  
    * Recompute vector embeddings

CLI Class:

* Methods:  
  * Run: Main program loop. Presents user with the following options  
    * Add activity:   
      * Run scope\_manager.\_add\_activity  
    * Delete activity: directly accesses schedule.\_remove\_activity  
      * Run scope\_manager.\_delete\_activity  
    * Add relationship: directly accesses schedule.\_add\_relationship  
      * Run scope\_manager.\_add\_relationship  
    * Delete relationship: directly accesses schedule.\_remove\_relationship  
      * Run scope manager.\_delete\_relationship  
    * Dissolve relationship:  
      * Run scope\_manager.\_dissolve\_relationship  
    * Open prompt:   
      * Run scope\_manager.\_dispatch  
    * Run schedule: does nothing for now  
    * Quit: Quits program

LLM Client Class: Provides functionality for parsing, tool calling, and open ended prompting 

* Methods:  
  * Prompt:  
    * Inputs:   
      * Messages: List of chat completion objects \[{‘role’: \<\>, ‘content’: \<\>}, …\]  
      * Model: OPENAI\_MODEL  
    * Outputs:  
      * Completion.choices\[0\].message.content: String form of completion  
    * Access via:  
      * Various  
  * Prompt with tools:  
    * Inputs:  
      * Messages: List of chat completion objects \[{‘role’: \<\>, ‘content’: \<\>}, …\]  
      * Model: OPENAI\_MODEL  
      * Tools: List of tool functions available to agent (from openai tool config file)  
    * Outputs:  
      * Completion.choices\[0\].message.tool\_calls  
  * Parse\_structured:  
    * Inputs  
      * Messages: List of chat completion objects \[{‘role’: \<\>, ‘content’: \<\>}, …\]  
      * Model: OPENAI\_MODEL  
      * Response format: pydantic type  
    * Outputs:  
      * completion.choices\[0\].message.parsed

Main: 

* On startup:  
  * Initializes CLI, schedule, and scope manager  
  * Calls CLI.run

