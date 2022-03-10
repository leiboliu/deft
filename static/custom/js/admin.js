function import_data(pid, d_id) {
        django.jQuery.ajax({
            url: 'ajax_import',
            method: 'GET',
            data: {'project_id': pid, 'dataset_id': d_id},
            success: function(data) {alert(data['status'])},
            error: function(data) {alert(data['status'])},

        });

    }

    function create_dirs(id) {
        django.jQuery.ajax({
            url: 'ajax_ops',
            method: 'GET',
            data: {'type': 'create', 'project_id': id},
            success: function(data) {
                console.log(data);
                alert(data['status']);
            },
            error: function(data) {alert(data['status'])},
        });
    }

    // function export_data(id, t){
    //     $.ajax({
    //         url: 'ajax_export',
    //         method: 'GET',
    //         data: {'id': id, 'type': t},
    //         success: function(data) {
    //             console.log(data);
    //             alert(data['stats']);
    //         },
    //         error: function(data) {alert(data['stats'])},
    //     });
    // }
