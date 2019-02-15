var vm = new Vue({
    el: '#process_overview',
    data: function() { 
        return {
            processes = []
        }
    },
    mounted: function(){
        var self = this;
        console.log(self);

        $.get('/list', function(data){
            self.processes = data;
            console.log(self.processes);
        }, 'json');
    }
})