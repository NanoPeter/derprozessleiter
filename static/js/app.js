var vm = new Vue({
    el: '#process_overview',
    data: function() {
        return {
            processes: {},
        }
    },
    methods: {
        stop: function(name){
            $.get('/process/'+name+'/stop')
        },
        restart: function(name){
            $.get('/process/'+name+'/restart')
        },
        start: function(name){
            $.get('/process/'+name+'/start')
        }
    },
    mounted: function(){
        var self = this;

        update_process = function(name){
            $.get('/process/'+name, function(data){
                Vue.set(self.processes, name, data);
            }, 'json');
        };

        $.get('/list', function(data){
            for (i = 0; i < data.length; i++){
                var name = data[i];
                console.log(name)
                Vue.set(self.processes, name, {'name': name})

                setInterval(update_process, 1000, name);
            }
            console.log(self);
        }, 'json');
    }
})