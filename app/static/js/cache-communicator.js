addCaching = (function communicator_namespace() {
  
    // Account create/view/edit
    
    function CacheCommunicator(source){
        this.source = source
        this.user = {}
    }
    
    function useSourceFor(funcName){
        CacheCommunicator.prototype[funcName] = function passBack(){
            return this.source[funcName].apply(this.source,arguments)
        }
    }
    
    
    [  
        "submitPhoto",
        "createIssue",
        "getIssue",
        "getIssues",
        "addNote",
        "updateIssue",
        "createAccount",
        "getAccounts",
        "updateAccount"
    ].map(useSourceFor, this)
    
    CacheCommunicator.prototype.signIn = function login(){
        console.log(this);
        return this.source.signIn.apply(this.source,arguments).then(function saveUser(user){
            this.user = user;
        }.bind(this));
    }
    
    CacheCommunicator.prototype.signOut = function logout(){
        return this.source.signOut.apply(this.source,arguments).then(function loggingOut(){
            this.user = {};
        }.bind(this));
    }
    
    function addCaching(communicator){
        return new CacheCommunicator(communicator)
    }

    return addCaching;
}());
