$('a#ProjectEdit').click(function (e) {
    let userEditURL = $(this).attr('data-ProjectEdit');
    e.preventDefault();
    $('#edit_project').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["project_edit_form"];
            $('#project-edit-form').html(form_string);
            $('#edit_project').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Project Edit Error --> ' + err);
        }
    });

});

$('a#EditTask').click(function (e) {
    let userEditURL = $(this).attr('data-EditTask');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["task_add_form"];
            $('#task_add_form').html(form_string);
            $('#edit_project').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Task Edit Error --> ' + err);
        }
    });

});

$('a#AddTask').click(function (e) {
    let userEditURL = $(this).attr('data-AddTask');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["task_add_form"];
            $('#add_task_form').html(form_string);
            $('#add_task_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Add Task Error --> ' + err);
        }
    });

});

$('a#TaskBoardEdit').click(function (e) {
    let userEditURL = $(this).attr('data-TaskBoardEdit');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["task_board_edit_form"];
            $('#edit_task_board_form').html(form_string);
            $('#edit_task_board').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Task Board Edit Error --> ' + err);
        }
    });

});

$('a#AddCard').click(function (e) {
    let userEditURL = $(this).attr('data-AddCard');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["add_card_form"];
            $('#add_card').html(form_string);
            $('#add_card_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Add Card Error --> ' + err);
        }
    });

});

$('a#EditCard').click(function (e) {
    let userEditURL = $(this).attr('data-EditCard');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["card_edit_form"];
            $('#edit_card').html(form_string);
            $('#edit_card_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Edit Card Error --> ' + err);
        }
    });

});


$('a#GetCard').click(function (e) {
    let userEditURL = $(this).attr('data-GetCard');
    e.preventDefault();
    $('#show_card_modal').modal('hide');
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["card_get_form"];
            $('#show_card').html(form_string);
            $('#show_card_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Get Card Error --> ' + err);
        }
    });

});

$('a#LeaveType').click(function (e) {
    let userEditURL = $(this).attr('data-LeaveType');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["leave_type_edit_form"];
            $('#edit_leavetype').html(form_string);
            $('#edit_leavetype_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Leave Type Error --> ' + err);
        }
    });

});


$('a#EditShift').click(function (e) {
    let userEditURL = $(this).attr('data-EditShift');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["shift_edit_form"];
            $('#edit_shift').html(form_string);
            $('#edit_shift_modal').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Edit Shift Error --> ' + err);
        }
    });

});

// update Policy on selection of Policy Type
$(document).on("change", '#id_policy_type', function (e) {
//$('#id_department').change(function (e) {
//     alert('hg');
    let polID = $(this).val();
    if (polID === '') {
        $('#id_policy').empty().append('<option value="" selected="">---------</option>');
        return;
    }
    let getURL = "/policies/" + polID + "/get/";
    // alert(getURL);
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let policies = response["policies"];
            // console.log(designations);

            $('#id_policy').empty().append('<option value="" selected="">---------</option>');
            for (let i = 0; i < policies.length; i++) {
                $('#id_policy').append(`
                    <option value="${policies[i][0]}">${policies[i][1]}</option>`);
            }
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});


// update Policy on selection of Policy Type
$(document).on("change", '#id_policy', function (e) {
//$('#id_claim').change(function (e) {
//     alert('hg');
    let polID = $(this).val();
    let policy = $('#id_policy_type').val();
    if (polID === '') {
        $('#customleave_select').empty().append('<option value="" selected="">---------</option>');
        $('#customleave_select_to').empty().append('<option value="" selected="">---------</option>');
        return;
    }
    let getURL = "/policyUser/" + polID + "/" + policy + "/get/";
    // alert(getURL);
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let users = response["users"];
            let nusers = response["nusers"];
            // console.log(designations);
            $('#customleave_select_to').empty();
            for (let i = 0; i < users.length; i++) {
                $('#customleave_select_to').append(`
                    <option value="${users[i][0]}">${users[i][1]}</option>`);
            }
            $('#customleave_select').empty();
            for (let i = 0; i < nusers.length; i++) {
                $('#customleave_select').append(`
                    <option value="${nusers[i][0]}">${nusers[i][1]}</option>`);
            }

        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});


$('a#EditLeave').click(function (e) {
    let userEditURL = $(this).attr('data-EditLeave');
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},
        success: function (response) {
            let form_string = response["leave_edit_form"];
            $('#edit_leave_form').html(form_string);
            $('#edit_leave').modal('show');
        },
        error: function (response) {
            let err = response["error"];
            alert('Edit Leave Error --> ' + err);
        }
    });

});

$(document).on("change", '#id_leave_type', function (e) {
    let leaveID = $('#id_leave_type').val();
    let userID = $('#id_user_id').val();
    let getURL = " /getRemainingDays/" + leaveID + "/" + userID + "/";
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},
        success: function (response) {
            let remaining_days = response["remaining_days"];
            $('#remaining_days_hidden').val(remaining_days);
            $('#remaining_days').val(remaining_days)
        }
    });
});

// Edit Claim Type
$('.claimEdit').on("click", function (e) {
    let claimEditURL = $(this).attr('data-claimEditURL');
    e.preventDefault();
    $('#edit_claim').modal({show: false});
    $.ajax({
        type: 'GET',
        url: claimEditURL,
        data: {},

        success: function (response) {
            let form_string = response["claim_form"];
            $('#claim-edit-form-div').html(form_string);
            $('#edit_claim').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// For Delete Claim type
$('.myDeleteClaimType').on("click", function (e) {
    e.preventDefault();
    let ClaimURL = $(this).attr('data-ClaimTypeDeleteURL');
    $("#DeleteClaimType").attr("href", ClaimURL);
});

// Edit Claim
$('.claimEdit').on("click", function (e) {
    let claimEditURL = $(this).attr('data-claimEditURL');
    e.preventDefault();
    $('#edit_claim').modal({show: false});
    $.ajax({
        type: 'GET',
        url: claimEditURL,
        data: {},

        success: function (response) {
            let form_string = response["claim_form"];
            $('#claim-edit-form-div').html(form_string);
            $('#edit_claim').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// For Delete Claim
$('.myDeleteClaim').on("click", function (e) {
    e.preventDefault();
    let ClaimURL = $(this).attr('data-ClaimDeleteURL');
    $("#DeleteClaim").attr("href", ClaimURL);
});


// Edit Claim
$('.claimFile').on("click", function (e) {
    let claimEditURL = $(this).attr('data-claimFileURL');
    e.preventDefault();
    $('#show_claim_files').modal({show: false});
    $.ajax({
        type: 'GET',
        url: claimEditURL,
        data: {},

        success: function (response) {
            let form_string = response["claim_files"];
            $('#claim-file-dive').html(form_string);
            $('#show_claim_files').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// Edit Manual Task Name
$('.manualTaskNameEdit').on("click", function (e) {
    let manualTaskNameEditURL = $(this).attr('data-manualTaskNameEditURL');
    e.preventDefault();
    $('#edit_manual_task_name').modal({show: false});
    $.ajax({
        type: 'GET',
        url: manualTaskNameEditURL,
        data: {},

        success: function (response) {
            let form_string = response["manual_task_name_form"];
            $('#manual-task-name-edit-form-div').html(form_string);
            $('#edit_manual_task_name').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// For Delete Manual Task Name
$('.myDeleteManualTaskName').on("click", function (e) {
    e.preventDefault();
    let ManualTaskNameURL = $(this).attr('data-ManualTaskNameDeleteURL');
    $("#DeleteManualTaskName").attr("href", ManualTaskNameURL);
});


// Edit Claim Type
$('.file_directoryEdit').on("click", function (e) {
    let file_directoryEditURL = $(this).attr('data-file_directoryEditURL');
    e.preventDefault();
    $('#edit_file_directory').modal({show: false});
    $.ajax({
        type: 'GET',
        url: file_directoryEditURL,
        data: {},

        success: function (response) {
            let form_string = response["file_directory_form"];
            $('#file_directory-edit-form-div').html(form_string);
            $('#edit_file_directory').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// For Delete Claim type
$('.myDeleteFileDirectoryType').on("click", function (e) {
    e.preventDefault();
    let FileDirectoryURL = $(this).attr('data-FileDirectoryTypeDeleteURL');
    $("#DeleteFileDirectoryType").attr("href", FileDirectoryURL);
});


// File Share With List
$('.FileShare').on("click", function (e) {
    let FileShareURL = $(this).attr('data-FileShare');
    e.preventDefault();
    $('#shared_with_user').modal({show: false});
    $.ajax({
        type: 'GET',
        url: FileShareURL,
        data: {},

        success: function (response) {
            let form_string = response["file_list_to_be_shared"];
            $('#shared_with_list').html(form_string);
            $('#shared_with_user').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

// For Delete Claim type
$('.DeletePerformance').on("click", function (e) {
    e.preventDefault();
    let PerformanceDeleteURL = $(this).attr('data-PerformanceDeleteURL');
    $("#DeletePerformanceLink").attr("href", PerformanceDeleteURL);
});


// update Policy on selection of Policy Type
// $().on("change", '#id_policy', function (e) {
//
//     e.preventDefault();
//     $.ajax({
//         type: 'GET',
//         url: getURL,
//         data: {},
//
//         success: function (response) {
//             let users = response["users"];
//             let nusers = response["nusers"];
//             $('#customleave_select_to').empty();
//             for (let i = 0; i < users.length; i++) {
//                 $('#customleave_select_to').append(`
//                     <option value="${users[i][0]}">${users[i][1]}</option>`);
//             }
//             $('#customleave_select').empty();
//             for (let i = 0; i < nusers.length; i++) {
//                 $('#customleave_select').append(`
//                     <option value="${nusers[i][0]}">${nusers[i][1]}</option>`);
//             }
//
//         },
//         error: function (response) {
//             // alert the error if any error occured
//             alert(response["responseJSON"]["error"]);
//         }
//     });
//
// });


// File Share With List
// $('.SpiderWebGraph').on("click", function (e) {
//     let SpiderWebGraphURL = $(this).attr('data-SpiderWebGraph');
//     e.preventDefault();
//     $('#shared_with_user').modal({show: false});
//     $.ajax({
//         type: 'GET',
//         url: SpiderWebGraphURL,
//         data: {},
//
//         success: function (response) {
//             let data = response["data"];
//             console.log(data, 'graph data')
//             Highcharts.chart('container', {
//
//                 chart: {
//                     polar: true,
//                     type: 'line'
//                 },
//
//                 accessibility: {
//                     description: 'A spiderweb chart compares the allocated '
//                 },
//
//
//                 title: {
//                     text: 'Performance Graph',
//                     x: -80
//                 },
//
//                 pane: {
//                     size: '80%'
//                 },
//
//                 xAxis: {
//                     categories: data[0].name,
//                     tickmarkPlacement: 'on',
//                     lineWidth: 0
//                 },
//
//                 yAxis: {
//                     gridLineInterpolation: 'polygon',
//                     lineWidth: 0,
//                     min: 0
//                 },
//
//                 tooltip: {
//                     shared: true,
//                     pointFormat: '<span style="color:{series.color}">{series.name}: <b>${point.y:,.0f}</b><br/>'
//                 },
//
//                 legend: {
//                     align: 'right',
//                     verticalAlign: 'middle',
//                     layout: 'vertical'
//                 },
//
//                 series: [{
//                     name: 'Allocated Budget',
//                     data: data[0].obtained,
//                     pointPlacement: 'on'
//                 }, {
//                     name: 'Actual Spending',
//                     data: data[0].total,
//                     pointPlacement: 'on'
//                 }],
//
//                 responsive: {
//                     rules: [{
//                         condition: {
//                             maxWidth: 500
//                         },
//                         chartOptions: {
//                             legend: {
//                                 align: 'center',
//                                 verticalAlign: 'bottom',
//                                 layout: 'horizontal'
//                             },
//                             pane: {
//                                 size: '70%'
//                             }
//                         }
//                     }]
//                 }
//
//             });
//         },
//         error: function (response) {
//             // alert the error if any error occured
//             let err = response["error"];
//             alert(err);
//         }
//     });
//
// });

$('#AllSharedWithUsers').on("click", function (e) {
    let checkedUsersIDs = [];
    $('input[name=permissions]:checked').each(function () {
        checkedUsersIDs.push($(this).val());
    });
    let roleID = $('#role_list li.active').attr('data-roleID');
    const roleData = {
        "roleID": roleID,
        "checkedUsersIDs": checkedUsersIDs,
        "csrfmiddlewaretoken": $('input[name=csrfmiddlewaretoken]').val()
    };
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: 'permission/update/',
        data: roleData,

        success: function (response) {
            let msg = response["success"];
            let msg_line = `
                    <div class="alert alert-dismissible fade show" role="alert">
                        <strong> ${msg} </strong>
                        <button type="button" class="close" data-dismiss="alert"aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                        </button>
                    </div>`;
            $('#msgline').prepend(msg_line);

        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });
});


$('#performance_list li').click(function (e) {
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
    let performanceID = $(this).attr('data-performanceID');
    // console.log(performanceID)
    let getURL = "/employee_performance_detail/" + performanceID + "/";
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let data = response["data"];
            let comment = response["comment"];
            // console.log(data)
            // console.log(comment)
            var chart = document.getElementById("highcarts_div");
            var payroll_main = document.getElementById("main_performance_div");
            chart.style.display = 'none';
            payroll_main.style.display = 'none';
            $('#AllPerformance').empty();

            let listPerms = $('#AllPerformance');
            listPerms.append(`<li>
            
                    <div class="d-flex">
                        <div class="card flex-fill">
                            <div class="card-body">
                                <h4 class="card-title">Review</h4>
                                    <div class="row">
                                        <div class="text-justify">
                                            <div class="mb-4">
                                                <p class="pl-3 pr-3">${comment}</p>
                                            </div>
                                        </div>
                                    </div>
                            </div>
                        </div>
                    </div>
                    <div class="table-responsive share-file-scroll">
                        <table class="table table-striped custom-table mb-0 datatable">
                            <thead>
                            <tr>
                                <th>Indicator Name</th>
                                <th>Obtained</th>
                                <th>Total</th>
                            </tr>
                            </thead>
                            <tbody id="performance-table-body">
                               
                            </tbody>
                        </table>
                    </div>
                                </li>`);
            chart.style.display = 'block';
            payroll_main.style.display = 'block';
            // console.log(data[0].name.length)
            let listTable = $('#performance-table-body');
            for (var i = 0; i < data[0].name.length; i++) {

                listTable.append(`<tr>
                                    <td>${data[0].name[i]}</td>
                                    <td>${data[0].obtained[i]}</td>
                                    <td>${data[0].total[i]}</td>
                                </tr>`
                )
            }
            new Highcharts.chart('container', {

                chart: {
                    polar: true,
                    type: 'line'
                },
                credits: {
                    enabled: false
                },

                accessibility: {
                    description: ''
                },


                title: {
                    text: 'Performance Graph',
                    x: -80
                },

                pane: {
                    size: '80%'
                },

                xAxis: {
                    categories: data[0].name,
                    tickmarkPlacement: 'on',
                    lineWidth: 0
                },

                yAxis: {
                    gridLineInterpolation: 'polygon',
                    lineWidth: 0,
                    min: 0
                },

                tooltip: {
                    shared: true,
                    pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
                },

                legend: {
                    align: 'right',
                    verticalAlign: 'middle',
                    layout: 'vertical'
                },

                series: [{
                    name: 'Obtained',
                    data: data[0].obtained,
                    pointPlacement: 'on'
                }, {
                    name: 'Total',
                    data: data[0].total,
                    pointPlacement: 'on'
                }],

                responsive: {
                    rules: [{
                        condition: {
                            maxWidth: 500
                        },
                        chartOptions: {
                            legend: {
                                align: 'center',
                                verticalAlign: 'bottom',
                                layout: 'horizontal'
                            },
                            pane: {
                                size: '70%'
                            }
                        }
                    }]
                }

            });

        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});