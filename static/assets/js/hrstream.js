// for sidebar menu highlighting
$(document).ready(function () {
    // $('#sidebar-list li').click(function (e) {
    //     $(this).siblings().removeClass('active');
    //     $(this).addClass('active');
    // });

    function highlightSidebar_setting() {
        $("#sidebar-list li a").each(function () {
            if ($(this).attr("href") === window.location.pathname) {
                $(this).parent('li').addClass("active");
            }
        });
    }

    highlightSidebar_setting();
});

// For formset
function updateElementIndex(el, prefix, ndx) {
    let id_regex = new RegExp('(' + prefix + '-\\d+)');
    let replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
    // {#alert(el.id + '   ' + el.name);#}
}

function addForm(btn, prefix, form_CssCls) {
    let formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    let row = $(form_CssCls + ':last').clone(true).get(0);
    $(row).removeAttr('id').insertAfter($(form_CssCls + ':last')).children('.hidden').removeClass('hidden');

    // {#console.log(row.children());#}
    // {#$(row).children().not(':last').children().each(function () {#}
    // {#    updateElementIndex(this, prefix, formCount);#}
    // {#    $(this).val('');#}
    // {# });#}

    $(row).find('input').each(function () {
        updateElementIndex(this, prefix, formCount);
        if (this.type !== 'hidden')
            $(this).val('');
    });

    $(row).find('.delete-row').click(function () {
        deleteForm(this, prefix, form_CssCls);
    });
    // {#console.log(row);#}
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    return false;
}

function deleteForm(btn, prefix, form_CssCls) {
    let row = $(btn).parents(form_CssCls);
    console.log(row);

    $(btn).parents(form_CssCls).remove(form_CssCls);
    let forms = $(form_CssCls);
    // {#console.log(forms);#}
    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
    for (let i = 0, formCount = forms.length; i < formCount; i++) {
        $(forms.get(i)).find('input').each(function () {
            updateElementIndex(this, prefix, i);
            // {#if (this.type !== 'hidden')#}
            // {#    $(this).val('');#}
        });
        // {#$(forms.get(i)).children().not(':last').children('input').each(function () {#}
        // {#    updateElementIndex(this, prefix, i);#}
        // {# });#}
    }
    return false;
}

// All these used for role&permissions
$('#saveRoleID').on("click", function (e) {
    let checkedIDs = [];
    $('input[name=permissions]:checked').each(function () {
        checkedIDs.push($(this).val());
    });
    let roleID = $('#role_list li.active').attr('data-roleID');
    const roleData = {
        "roleID": roleID,
        "checkedIDs": checkedIDs,
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
$('.action-circle').on("click", function (e) {
    e.preventDefault();
    let roleURL = $(this).attr('data-roleEditURL');
    let role_name = $(this).parent().parent().attr('data-roleName');
    $("#edit_role_form").attr("action", roleURL);
    $('input[name="role_name"]').val(role_name);

});
$('.myDeleteRole').on("click", function (e) {
    e.preventDefault();
    let roleURL = $(this).attr('data-roleDeleteURL');
    $("#DeleteRole").attr("href", roleURL);
});
$('#role_list li').click(function (e) {
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
    let roleID = $(this).attr('data-roleID');
    let getURL = "/role/" + roleID + "/get";
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let permsChecked = response["perms_checked"];
            let allPerms = response["all_perms"];
            $('#AllPermissions li').each(function () {
                    $(this).remove();
                }
            );
            let listPerms = $('#AllPermissions');
            let i, j;
            for (i = 0, j = 0; i < allPerms.length; i++) {
                if (j < permsChecked.length && allPerms[i][1] === permsChecked[j][1]) {
                    if (allPerms[i][1] === 'basic') {
                        listPerms.append(`<li class="list-group-item">
                                ${allPerms[i][2]}
                                    <div class="status-toggle">
                                        <input name="permissions" value="${allPerms[i][0]}" type="checkbox" id="${allPerms[i][1]}_module" class="check"
                                              checked="checked" disabled="disabled">
                                         <label for="${allPerms[i][1]}_module" class="checktoggle">checkbox</label>
                                    </div>
                                </li>`);
                    } else {
                        listPerms.append(`<li class="list-group-item">
                                ${allPerms[i][2]}
                                    <div class="status-toggle">
                                        <input name="permissions" value="${allPerms[i][0]}" type="checkbox" id="${allPerms[i][1]}_module" class="check"
                                              checked="checked">
                                         <label for="${allPerms[i][1]}_module" class="checktoggle">checkbox</label>
                                    </div>
                                </li>`);
                    }
                    j++;
                } else {
                    listPerms.append(`<li class="list-group-item">
                                ${allPerms[i][2]}
                                    <div class="status-toggle">
                                        <input name="permissions" value="${allPerms[i][0]}" type="checkbox" id="${allPerms[i][1]}_module" class="check"
                                              >
                                         <label for="${allPerms[i][1]}_module" class="checktoggle">checkbox</label>
                                    </div>
                                </li>`);
                }
            }
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});

// For Edit Department
// $('.departmentEdit').on("click", function (e) {
//     // e.preventDefault();
//     let depURL = $(this).attr('data-depEditURL');
//     $("#edit_dep_form").attr("action", depURL);
//
//
// });

//payrolls
$('#payroll_list li').click(function (e) {
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
    let payrollID = $(this).attr('data-payrollID');
    let getURL = "/payroll_detail/" + payrollID + "/get";
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let payroll = response["payroll"];
            let percentage_data = response["data_list"];
            var chart = document.getElementById("highcarts_div");
            var payroll_main = document.getElementById("main_payroll_div");
            chart.style.display = 'none';
            payroll_main.style.display = 'none';
            $('#AllPayroll').empty();
            $('#payroll_taxes li').each(function () {
                $(this).remove();
            });
            $('#payroll_benefit li').each(function () {
                $(this).remove();
            });
            $('#payroll_deductions li').each(function () {
                $(this).remove();
            });

            let listPerms = $('#AllPayroll');
            listPerms.append(`<li>
                                <div id="accordion">
                                <div class="card">
                                <div class="card-body">
                                <div class="panel-body pl-4"><strong>Gross Salary </strong> 
                                <span class="float-right pr-4">${payroll[0].gross_salary}</span>
                                </div>
                                </div>
                                </div>
                                <div class="card">
                                <div class="card-body">                    
                                <strong class="pl-4">Net Salary</strong>
                                <span class="float-right pr-4">${payroll[0].net_salary}</span>
                                </div>
                                </div>
                                <div class="card">
                                <div class="card-body">                    
                                <strong class="pl-4">401k amount</strong>
                                <span class="float-right pr-4">${payroll[0].amount_401K}</span>
                                </div>
                                </div>
                                </div>
                                 <div id="accordion_adjustment">
                                <div class="card" id="texes_card">
                                <div class="card-header" id="headingTaxes">
                                        <h5 class="mb-0">
                                            <button class="btn  collapsed" data-toggle="collapse"
                                                    data-target="#collapseTaxes" aria-expanded="false"
                                                    aria-controls="collapseTaxes">
                                                <strong>Taxes</strong>
                                            </button>
                                       </h5>
                                    </div>
                                <div class="collapse" aria-labelledby="headingTaxes" id="collapseTaxes"
                                         data-parent="#accordion_adjustment">
                                        <div id="collapseTaxes" class="card-body">
                                            <ul id="payroll_taxes" class="list-unstyled">
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div class="card" id="benefit_card">
                                <div class="card-header" id="headingBenefit">
                                        <h5 class="mb-0">
                                            <button class="btn  collapsed" data-toggle="collapse"
                                                    data-target="#collapseBenefit" aria-expanded="false"
                                                    aria-controls="collapseBenefit">
                                                <strong>Payroll Benefit</strong>
                                            </button>
                                        </h5>
                                    </div>
                                <div class="collapse" aria-labelledby="headingBenefit" id="collapseBenefit"
                                         data-parent="#accordion_adjustment">
                                        <div id="collapseBenefit" class="card-body">
                                            <ul id="payroll_benefit" class="list-unstyled">
                                            </ul>
                                       </div>
                                    </div>
                                </div>
                                <div class="card" id="deduction_card">
                                <div class="card-header" id="headingDeduction">
                                        <h5 class="mb-0">
                                            <button class="btn  collapsed" data-toggle="collapse"
                                                    data-target="#collapseDeduction" aria-expanded="false"
                                                    aria-controls="collapseDeduction">
                                                <strong>Payroll Deduction</strong>
                                            </button>
                                        </h5>
                                    </div>
                                <div class="collapse" aria-labelledby="headingDeduction" id="collapseDeduction" data-parent="#accordion_adjustment">
                                <div id="collapseDeduction" class="card-body">
                                            <ul id="payroll_deductions" class="list-unstyled">
                                            </ul>
                                        </div>
                                </div>
                                </div>
                                <div class="card" id="claim_card">
                                <div class="card-header" id="headingClaim">
                                        <h5 class="mb-0">
                                            <button class="btn  collapsed" data-toggle="collapse"
                                                    data-target="#collapseClaim" aria-expanded="false"
                                                    aria-controls="collapseClaim">
                                                <strong>Payroll Claim</strong>
                                            </button>
                                        </h5>
                                    </div>
                                <div class="collapse" aria-labelledby="headingClaim" id="collapseClaim"
                                         data-parent="#accordion_adjustment">
                                        <div id="collapseClaim" class="card-body">
                                            <ul id="payroll_claims" class="list-unstyled">
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                </div>
                                </li>`);
            let tax_count = 0;
            let benefit_count = 0;
            let deduction_count = 0;
            let claim_count = 0;
            let listTaxes = $('#payroll_taxes');
            let listBenefit = $('#payroll_benefit');
            let listDeduction = $('#payroll_deductions');
            let listClaim = $('#payroll_claims');
            var tax_hide = document.getElementById("taxes_card");
            var benefit_hide = document.getElementById("benefit_card");
            var deduction_hide = document.getElementById("deduction_card");
            var claim_hide = document.getElementById("claim_card");
            chart.style.display = 'block';
            payroll_main.style.display = 'block';

            for (var i = 0; i < payroll[0].payroll_tax.length; i++) {
                tax_count++;
                listTaxes.append(`
                <li class="pl-4"><strong>${payroll[0].payroll_tax[i].name} ( ${payroll[0].payroll_tax[i].percentage} %)</strong>
                 <span class="float-right pr-4">$ ${payroll[0].payroll_tax[i].tax_amount}</span>
                 </li>`)

            }

            for (var j = 0; j < payroll[0].salary_adjustment.length; j++) {
                if (payroll[0].salary_adjustment[j].adjustment_type === 'benefit') {
                    benefit_count++;
                    listBenefit.append(`
                <li class="pl-4"><strong>${payroll[0].salary_adjustment[j].name}</strong>
                 <span class="float-right pr-4">$ ${payroll[0].salary_adjustment[j].amount}</span>
                 </li>`)
                }
                if (payroll[0].salary_adjustment[j].adjustment_type === 'deduction') {
                    deduction_count++;
                    listDeduction.append(`
                <li class="pl-4"><strong>${payroll[0].salary_adjustment[j].name}</strong>
                 <span class="float-right pr-4">$ ${payroll[0].salary_adjustment[j].amount}</span>
                 </li>`)
                }
                if (payroll[0].salary_adjustment[j].adjustment_type === 'claim') {
                    claim_count++;
                    listClaim.append(`
                <li class="pl-4"><strong>${payroll[0].salary_adjustment[j].name}</strong>
                 <span class="float-right pr-4">$ ${payroll[0].salary_adjustment[j].amount}</span>
                 </li>`)
                }
            }

            Highcharts.chart('container', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: 'Payroll Detail'
                }, credits: {
                    enabled: false
                },
                tooltip: {
                    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                        }
                    }
                },
                series: [{
                    name: 'Payroll',
                    colorByPoint: true,
                    data: percentage_data
                }]
            });
            if (claim_count === 0) {
                claim_hide.style.display = 'none'
            }
            if (benefit_count === 0) {
                benefit_hide.style.display = 'none'
            }
            if (deduction_count === 0) {
                deduction_hide.style.display = 'none'
            }
            if (tax_count === 0) {
                tax_hide.style.display = 'none'
            }

        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});


// <li class="list-group-item">
//                                                     <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       Gross Salary<span class="float-right">${payroll[0].fields.gross_salary}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//                                          <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       Net Salary<span class="float-right">${payroll[0].fields.net_salary}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//                                         <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       401K Amount<span class="float-right">${payroll[0].fields._401K_amount}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//                                             <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       401K Amount<span class="float-right">${payroll[0].fields._401K_amount}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//
//                                             <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       Working Hour<span class="float-right">${payroll[0].fields.working_hours}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//
//                                             <div class="panel-group" id="accordion">
//                                               <div class="panel panel-default">
//                                                 <div class="panel-heading">
//                                                   <h4 class="panel-title">
//                                                       Leave Hour<span class="float-right">${payroll[0].fields.leave_hours}</span>
//                                                   </h4>
//                                                 </div>
//                                               </div>
//                                             </div>
//
//                                         </li>
$('.departmentEdit').on("click", function (e) {
    let depEditURL = $(this).attr('data-depEditURL');
    e.preventDefault();
    $('#edit_department').modal({show: false});
    $.ajax({
        type: 'GET',
        url: depEditURL,
        data: {},

        success: function (response) {
            let form_string = response["department_form"];
            $('#department-edit-form-div').html(form_string);
            $('#edit_department').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// For Delete Department
$('.myDeleteDepartment').on("click", function (e) {
    e.preventDefault();
    let DepURL = $(this).attr('data-DepartmentDeleteURL');
    $("#DeleteDepartment").attr("href", DepURL);
});
// For Edit Designation
// $('.myEditDesignation').on("click", function (e) {
//     // e.preventDefault();
//     let designID = $(this).attr('data-DesignID');
//     let designEditURL = "/designation/" + designID + "/edit/";
//     // alert(designEditURL);
//     $("#edit_design_form").attr("action", designEditURL);
// });

$('.myEditDesignation').on("click", function (e) {
    let designID = $(this).attr('data-DesignID');
    let designEditURL = "/designation/" + designID + "/edit/";
    // alert(designEditURL);
    e.preventDefault();
    $('#edit_designation').modal({show: false});
    $.ajax({
        type: 'GET',
        url: designEditURL,
        data: {},

        success: function (response) {
            let form_string = response["designation_form"];
            $('#designation-form-div').html(form_string);
            $('#edit_designation').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

// For Delete Designation
$('.myDeleteDesignation').on("click", function (e) {
    e.preventDefault();
    let DgnURL = $(this).attr('data-DesignationDeleteURL');
    // alert(DgnURL);
    $("#DeleteDesignation").attr("href", DgnURL);
});

// For Delete Equipment
$('.DeleteEquipment').on("click", function (e) {
    e.preventDefault();
    let EqpURL = $(this).attr('data-EquipmentDeleteURL')
    $("#DeleteEquipment").attr("Data-DeleteEquipmentClick", EqpURL);
    $("#delete_asset").modal('show');
});

// update Designations on selection of department
$(document).on("change", '#id_department', function (e) {
//$('#id_department').change(function (e) {
//     alert('hg');
    let depID = $(this).val();
    if (depID === '') {
        $('#id_designation').empty().append('<option value="" selected="">---------</option>');
        return;
    }
    let getURL = "/designation/" + depID + "/get/";
    // alert(getURL);
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let designations = response["designations"];
            // console.log(designations);
            $('#id_designation').empty();
            for (let i = 0; i < designations.length; i++) {
                $('#id_designation').append(`
                    <option value="${designations[i][0]}">${designations[i][1]}</option>`);
            }
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});


// update Tasks on selection of project
$(document).on("change", '#id_project', function (e) {
//$('#id_department').change(function (e) {
//     alert('hg');
    let proID = $(this).val();
    // alert(proID)
    if (proID === '') {
        $('#id_task').empty().append('<option value="" selected="">---------</option>');
        return;
    }
    let getURL = "/task/" + proID + "/get";
    // alert(getURL);
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: getURL,
        data: {},

        success: function (response) {
            let tasks = response["tasks"];
            $('#id_task').empty();
            for (let i = 0; i < tasks.length; i++) {
                $('#id_task').append(`
                    <option value="${tasks[i][0]}">${tasks[i][1]}</option>`);
            }
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});

// Resend On-Boarding Link
$('#resendOnBoardingLink').click(function (e) {
    let resendURL = $(this).attr('data-OnboardResendLinkURL');
    // alert(resendURL);
    // return;
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: resendURL,
        data: {},

        success: function (response) {
            let msg = response["success"];
            let msg_line = `
                    <div class="alert alert-dismissible fade show" role="alert">
                        <strong> ${msg} </strong>
                        <button type="button" class="close" data-dismiss="alert"aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                        </button>
                    </div>`;
            $('#allEmployeesMessages').prepend(msg_line);
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    });

});

// User Profile Edit Form
$('.profile-view').click(function (e) {
    let userEditURL = $(this).attr('data-UserProfileEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["user_profile_form"];
            $('#user_form_div').html(form_string);
            $('#profile_info').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

// User Personal Info Edit Form
$('a#UserPersonalInfoEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserPersonalInfoEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#personal_info_modal').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["user_personalinfo_form"];
            $('#user_personalinfo_form').html(form_string);
            $('#personal_info_modal').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Personal Info Error --> ' + err);
        }
    });

});

// User Personal Info Edit Form
$('a#UserBankInfoEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserBankInfoEditURL');
    //alert(userEditURL);
    e.preventDefault();
    $('#bank_info_modal').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["user_bank_info_form"];
            $('#user_bankinfo_form').html(form_string);
            $('#bank_info_modal').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Bank Info Error --> ' + err);
        }
    });

});

// User Emergency Contact Edit Form
$('a#UserEmergencyContactEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserEmergencyContactEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#emergency_contact_modal').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["user_emergency_contact_form"];
            $('#user_emergency_contact_form').html(form_string);
            $('#emergency_contact_modal').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Personal Info Error --> ' + err);
        }
    });

});

// User Education Info Edit Form
$('a#UserEducationInfoEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserEducationInfoEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#education_info').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["user_education_info_form"];
            $('#user_education_info_form').html(form_string);
            $('#education_info').modal('show');
            // abc();
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Education Info Error --> ' + err);
        }
    });

});

// User Experience Edit Form
$('a#UserExperienceEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserExperienceEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#experience_info').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["employee_experience_form"];
            $('#user_experience_form').html(form_string);
            $('#experience_info').modal('show');
            // abc();
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Experience Error --> ' + err);
        }
    });

});

// User Document Edit Form
$('a#UserDocumentEdit').click(function (e) {
    let userEditURL = $(this).attr('data-UserDocumentEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#documents_info').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["employee_document_form"];
            $('#user_documents_form').html(form_string);
            $('#documents_info').modal('show');
            // abc();
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Document Error --> ' + err);
        }
    });

});

// User Salary Edit Form
$('.EditUserSalary').click(function (e) {
    let userEditURL = $(this).attr('data-EditSalaryURL');
    //alert(userEditURL);
    e.preventDefault();
    $('#edit_user_salary_modal').modal({show: false});
    $.ajax({
        type: 'GET',
        url: userEditURL,
        data: {},

        success: function (response) {
            let form_string = response["salary_edit_form"];
            $('#edit_salary').html(form_string);
            $('#edit_user_salary_modal').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// Client Edit Form
$('a#ClientProfileEdit').click(function (e) {
    let clientEditURL = $(this).attr('data-ClientProfileEditURL');
    // alert(userEditURL);
    e.preventDefault();
    $('#client_profile').modal({show: false});
    $.ajax({
        type: 'GET',
        url: clientEditURL,
        data: {},

        success: function (response) {
            let form_string = response["client_edit_form"];
            $('#client_form_div').html(form_string);
            $('#client_profile').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert('Client Profile Error --> ' + err);
        }
    });

});

function previewFile(img) {
    const preview = document.querySelector('#' + img.id);
    const file = document.querySelector('#id_profile_pic').files[0];
    const reader = new FileReader();

    reader.addEventListener("load", function () {
        // convert image file to base64 string
        preview.src = reader.result;
    }, false);

    if (file) {
        reader.readAsDataURL(file);
    }
    return false;
}

// ========================================================================================================
// Formset for Education Info
// ========================================================================================================

// $('.changeNumber').each(function (e) {
//     $(this).html(parseInt($('.changeNumber').html(), 10)+1)
// });


var notificationTimeout;

//Shows updated notification popup
var updateNotification = function (task, notificationText, newClass) {
    var notificationPopup = $('.notification-popup ');
    notificationPopup.find('.task').text(task);
    notificationPopup.find('.notification-text').text(notificationText);
    notificationPopup.removeClass('hide success');
    // If a custom class is provided for the popup, add It
    if (newClass)
        notificationPopup.addClass(newClass);
    // If there is already a timeout running for hiding current popup, clear it.
    if (notificationTimeout)
        clearTimeout(notificationTimeout);
    // Init timeout for hiding popup after 3 seconds
    notificationTimeout = setTimeout(function () {
        notificationPopup.addClass('hide');
    }, 9000);
};

// calculate number of days between two dates
$('#id_leave_from, #id_leave_to').change(function () {


    if ($('#id_leave_from').val() && $('#id_leave_to').val()) {
        var startDate = new Date($('#id_leave_from').val());
        var endDate = new Date($('#id_leave_to').val());
        var todayDate = new Date($('#to_day_date').val());

        if (startDate > endDate) {
            updateNotification(startDate, '  grater than End Date.');
            $('#id_leave_to').val(todayDate);
            $('#id_requested_days').val("")

        } else {
            var days = calcDaysBetween(startDate, endDate);
            days = days + 1;
            var remaining_days = $('#remaining_days_hidden').val();

            $('#id_requested_days').val(days);
            $('#remaining_days').val(parseInt(remaining_days) - parseInt(days));
            if (todayDate > startDate) {
                updateNotification(startDate, '  is from Future. Can not apply form Future date.');
                $('#id_leave_from').val(startDate);
                $('#id_requested_days').val('');
                $('#remaining_days').val('');
            }
            if (todayDate > endDate) {
                updateNotification(startDate, '  is from Past. Can not apply form Past date.');
                $('#id_leave_to').val(startDate);
                $('#id_requested_days').val('');
            }
            if ($('#remaining_days').val() < 0) {
                updateNotification(remaining_days, 'Remaining Days./n/' + days + '  days Exceeded Remaining days limit.Please Apply Within Remaining Days.');
                $('#id_leave_from').val(startDate)
                $('#id_leave_to').val(startDate)
                $('#id_requested_days').val('')
                $('#remaining_days').val('')

            }
        }
    }
});
// $('#id_leave_from, #id_leave_to').change(function () {
//
//
//     if ($('#id_leave_from').val() && $('#id_leave_to').val()) {
//         var startDate = new Date($('#id_leave_from').val())
//         var endDate = new Date($('#id_leave_to').val())
//         var todayDate = new Date($('#to_day_date').val())
//
//         if (startDate > endDate) {
//              updateNotification(startDate, '  grater than End Date.');
//              $('#id_leave_to').val(todayDate)
//             $('#id_requested_days').val("")
//
//         } else {
//             var days = calcDaysBetween(startDate, endDate)
//             var remaining_days = $('#remaining_days_hidden').val()
//
//             $('#id_requested_days').val(days)
//             $('#remaining_days').val(parseInt(remaining_days) - parseInt(days))
//             if (todayDate > startDate) {
//                 updateNotification(startDate, '  is from Future. Can not apply form Future date.');
//                 $('#id_leave_from').val(startDate)
//                 $('#id_requested_days').val('')
//                 $('#remaining_days').val('')
//             }
//             if (todayDate > endDate) {
//                  updateNotification(startDate, '  is from Past. Can not apply form Past date.');
//                 $('#id_leave_to').val(startDate)
//                 $('#id_requested_days').val('')
//                 $('#remaining_days').val('')
//             }
//
//             if ($('#remaining_days').val() < 0) {
//                  updateNotification(remaining_days, '  days Exceeded Remaining Days.Please Apply Within Remaining Days.');
//                 $('#id_leave_from').val(startDate)
//                 $('#id_leave_to').val(startDate)
//                 $('#id_requested_days').val('')
//                 $('#remaining_days').val('')
//
//             }
//         }
//     }
// });


$('#id_leave_from_edit, #id_leave_to_edit').change(function () {


    if ($('#id_leave_from_edit').val() && $('#id_leave_to_edit').val()) {
        var startDate = new Date($('#id_leave_from_edit').val())
        var endDate = new Date($('#id_leave_to_edit').val())

        if (startDate > endDate) {
            alert('Invalid dates');
            $('#id_requested_days_edit').val("")

        } else {
            var days = calcDaysBetween(startDate, endDate)
            var remaining_days = $('#remaining_days_edit').val()

            $('#id_requested_days_edit').val(days)
            $('#remaining_days_edit').val(parseInt(remaining_days) - parseInt(days))
        }
    }
});

function calcDaysBetween(startDate, endDate) {

    return (endDate - startDate) / (1000 * 60 * 60 * 24)

}


$('#switch_round_off').change(function () {
    if ($('#hidden_portion').css('display') == 'none') {
        alert($('#hidden_portion').css('display'));
        $('#hidden_portion').css('display', 'block');
    } else {
        alert($('#hidden_portion').css('display'));
        $('#hidden_portion').css('display', 'none');
    }
});

function printPageArea(areaID) {
    var printContent = document.getElementById(areaID);
    var WinPrint = window.open('', '', 'width=900,height=650');
    WinPrint.document.write(printContent.innerHTML);
    WinPrint.document.close();
    WinPrint.focus();
    WinPrint.print();
    WinPrint.close();
}

// edit time log table
$('.timeLogEdit').on("click", function (e) {
    let timeEditURL = $(this).attr('data-timeEditURL');
    e.preventDefault();
    $('#edit_timeLog').modal({show: false});
    $.ajax({
        type: 'GET',
        url: timeEditURL,
        data: {},

        success: function (response) {
            let form_string = response["timeLog_form"];
            $('#timeLog-edit-form-div').html(form_string);
            $('#edit_timeLog').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// edit equipment
$('.EditEquipment').on("click", function (e) {
    let equipmentEditUrl = $(this).attr('data-EquipmentEditURL');
    e.preventDefault();
    $('#edit_asset').modal({show: false});
    $.ajax({
        type: 'GET',
        url: equipmentEditUrl,
        data: {},

        success: function (response) {
            let form_string = response["equipment_edit_form"];
            $('#equipment_edit_form').html(form_string);
            $('#edit_asset').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


// edit timeLog
$('.timeLogDelete').on("click", function (e) {
    let Url = $(this).attr('data-timeDeleteURL');
    e.preventDefault();
    $('#delete_time_log_table').attr("href", Url);
});


// edit equipment
$('.payrollItemDelete').on("click", function (e) {
    let payrollItemDeleteUrl = $(this).attr('data-PayrollItemDelete');
    e.preventDefault();
    $.ajax({
        type: 'Get',
        url: payrollItemDeleteUrl,
        data: {},

        success: function (response) {
            let item = document.getElementById(response['payroll_item_type'] + '-' + response['pk'])
            item.style.display = 'none';
            $("#DeletePayrollItemClick").attr("data-PayrollItemDelete", "");
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

$('.myDeletePayrollItem').on("click", function (e) {
    e.preventDefault();
    let myDeletePayrollItemURL = $(this).attr('data-PayrollItemDeleteURL');
    $("#DeletePayrollItemClick").attr("href", myDeletePayrollItemURL);
});

$('.myDeletePayrollTax').on("click", function (e) {
    e.preventDefault();
    let myDeletePayrollItemURL = $(this).attr('data-PayrollTaxDeleteURL');
    $("#DeletePayrollTaxClick").attr("href", myDeletePayrollItemURL);
});

$('.payrollTaxDelete').on("click", function (e) {
    let payrollItemDeleteUrl = $(this).attr('data-PayrollTaxDelete');
    e.preventDefault();
    $.ajax({
        type: 'Get',
        url: payrollItemDeleteUrl,
        data: {},

        success: function (response) {
            let item = document.getElementById('tax-' + response['pk'])
            item.style.display = 'none';
            $("#DeletePayrollTaxlick").attr("data-PayrollItemDelete", "");
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});
$('#equipment-search-form').on('submit', function (e) {
    e.preventDefault();
    $('#equipment-search-table tr').each(function () {
        $(this).remove();
    });
    const searchTable = $('#equipment-search-table');

    $.ajax({
        type: 'POST',
        url: '/equipment_search/',
        data: $(this).serialize(),

        success: function (response) {
            debugger;
            let equipments = response['equipments'];

            // console.log(equipments[0].equipment, 'equipments');
            // console.log(equipments[0].user_object['username'], 'user object');
            for (let i = 0; i <= equipments.length; i++) {
                // let  assign_to_profile = `<img src="../../static/assets/img/user.jpg" alt=""/>`;
                // if (equipments[i].user_object.profile_pic){
                // assign_to_profile = `<img src="../../media/"${equipments[i].user_object['profile_pic']} alt=""/>`;}
                // // <a href="javascript:void(0);" class="avatar avatar-xs">${assign_to_profile}</a>
                // console.log(assign_to_profile, 'length');
                let assign_to_main = ``
                if (equipments[i].equipment['assign_to_id']) {
                    assign_to_main = `<h2 class="table-avatar"><a href="javascript:void(0);">${equipments[i].user_object['first_name']} ${equipments[i].user_object['first_name']}</a> </h2>`;
                }
                let i_tag = '';
                if (equipments[i].equipment['status'] === 'New') {
                    i_tag = `<i class="fa fa-dot-circle-o text-purple"></i>`
                } else if (equipments[i].equipment['status'] === 'Assigned') {
                    i_tag = `<i class="fa fa-dot-circle-o text-info"></i>`
                } else if (equipments[i].equipment['status'] === 'Deployed') {
                    i_tag = `<i class="fa fa-dot-circle-o text-success"></i>`
                } else if (equipments[i].equipment['status'] === 'Stocked') {
                    i_tag = `<i class="fa fa-dot-circle-o text-danger"></i>`
                } else if (equipments[i].equipment['status'] === 'Damaged') {
                    i_tag = `<i class="fa fa-dot-circle-o text-purple"></i>`
                }
                // console.log(i_tag, 'i tag')
                // console.log(equipments[i].equipment['status'], 'i tag')
                searchTable.append(`<tr><td>` + assign_to_main + `</td><td><strong>${equipments[i].equipment['name']}</strong></td>
            <td>${equipments[i].equipment['equipment_code']}</td>
            <td>${equipments[i].equipment['purchase_date']}</td>
            <td>${equipments[i].equipment['description']}</td>
            <td>${equipments[i].equipment['price']}</td>
            <td class="text-center">
                                        <div class="dropdown action-label">
                                            <a class="btn btn-white btn-sm btn-rounded dropdown-toggle" href=""
                                               data-toggle="dropdown" aria-expanded="false">
                                               ${i_tag}
                                             ${equipments[i].equipment['status']}
                                            </a>
                                            <div class="dropdown-menu dropdown-menu-right">
                                                <a class="dropdown-item"
                                                   href="/equipment_status/${equipments[i].equipment['id']}/Stocked"><i
                                                        class="fa fa-dot-circle-o text-danger"></i> Stocked</a>
                                                <a class="dropdown-item"
                                                   href="/equipment_status/${equipments[i].equipment['id']}/Deployed'"><i
                                                        class="fa fa-dot-circle-o text-success"></i> Deployed</a>
                                                <a class="dropdown-item"
                                                   href="/equipment_status/${equipments[i].equipment['id']}/Assigned"><i
                                                        class="fa fa-dot-circle-o text-info"></i> Assigned</a>
                                                <a class="dropdown-item"
                                                   href="/equipment_status/${equipments[i].equipment['id']}/Damaged"><i
                                                        class="fa fa-dot-circle-o text-purple"></i> Damaged</a>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="text-right">
                                        <div class="dropdown dropdown-action">
                                            <a href="javascript:void(0)" class="action-icon dropdown-toggle"
                                               data-toggle="dropdown" aria-expanded="false"><i class="material-icons">more_vert</i></a>
                                            <div class="dropdown-menu dropdown-menu-right">
                                                <a class="dropdown-item EditEquipment" href="javascript:void(0)"
                                                   data-EquipmentEditURL="/equipment_edit/${equipments[i].equipment['id']}/"
                                                   data-toggle="modal" data-target="#edit_asset"><i
                                                        class="fa fa-pencil m-r-5"></i> Edit</a>
                                                <a class="dropdown-item DeleteEquipment" href="javascript:void(0)"
                                                   data-EquipmentDeleteURL="/equipment_delete/${equipments[i].equipment['id']}"
                                                   data-toggle="modal" data-target="#delete_asset"><i
                                                        class="fa fa-trash-o m-r-5"></i> Delete</a>
                                            </div>
                                        </div>
                                    </td>
                                    </tr>`);
            }
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });
})

$('.equipmentDeleteClick').on("click", function (e) {
    let payrollItemDeleteUrl = $(this).attr('Data-DeleteEquipmentClick');
    // console.log(payrollItemDeleteUrl, 'url')
    e.preventDefault();
    $.ajax({
        type: 'Get',
        url: payrollItemDeleteUrl,
        data: {},

        success: function (response) {
            let item = document.getElementById('equipment-' + response['pk'])
            // console.log(item);
            item.style.display = 'none';
            $("#DeleteEquipment").attr("Data-DeleteEquipmentClick", "");
            $("#delete_asset").modal('hide');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

$('.myDeleteBookmark').on("click", function (e) {
    e.preventDefault();
    let myDeleteBookmarkURL = $(this).attr('data-BookmarkDeleteURL');
    $("#DeleteBookmark").attr("href", myDeleteBookmarkURL);
});


// edit Bookmark
$('.EditBookmark').on("click", function (e) {
    let bookmarkEditUrl = $(this).attr('data-BookmarkEditURL');
    e.preventDefault();
    $('#edit_bookmark').modal({show: false});
    $.ajax({
        type: 'GET',
        url: bookmarkEditUrl,
        data: {},

        success: function (response) {
            let form_string = response["bookmark_edit_form"];
            $('#bookmark_edit_form').html(form_string);
            $('#edit_bookmark').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});

// indicator delete

$('.IndicatorDelete').on("click", function (e) {
    e.preventDefault();
    let DeleteIndicatorURL = $(this).attr('data-IndicatorDelete');
    // console.log(DeleteIndicatorURL)
    $("#IndicatorDeleteLink").attr("href", DeleteIndicatorURL);
});


// edit indicator

$('.EditIndicator').on("click", function (e) {
    let IndicatorEditUrl = $(this).attr('data-IndicatorEditURL');
    e.preventDefault();
    $('#edit_indicator').modal({show: false});
    $.ajax({
        type: 'GET',
        url: IndicatorEditUrl,
        data: {},

        success: function (response) {
            let form_string = response["indicator_edit_form"];
            $('#indicator_edit_form').html(form_string);
            $('#edit_indicator').modal('show');
        },
        error: function (response) {
            // alert the error if any error occured
            let err = response["error"];
            alert(err);
        }
    });

});


$(document).ready(function () {
    if (localStorage.getItem('color') != null) {
        document.documentElement.style.setProperty('--dark-color', localStorage.getItem('color'));
        document.documentElement.style.setProperty('--darker-color', localStorage.getItem('color_darker'));
        document.documentElement.style.setProperty('--light-color', localStorage.getItem('light_color'));
        document.documentElement.style.setProperty('--hover-color', localStorage.getItem('hover_color'));
        document.documentElement.style.setProperty('--menu-list-color', localStorage.getItem('menu_list_color'));
    }

})

const colors = document.getElementsByClassName('colors');
var i;
for (i = 0; i < colors.length; i++) {
    colors[i].addEventListener('click', changeColor);
}

function changeColor() {
    let color = this.getAttribute('data-color');
    let light_color = this.getAttribute('data-color-lighter');
    let hover_color = this.getAttribute('data-color-hover');
    let menu_list_color = this.getAttribute('data-menu-list');
    localStorage.setItem('color', color)
    localStorage.setItem('color_darker', color)
    localStorage.setItem('light_color', light_color)
    localStorage.setItem('hover_color', hover_color)
    localStorage.setItem('menu_list_color', menu_list_color)
    document.documentElement.style.setProperty('--dark-color', color);
    document.documentElement.style.setProperty('--darker-color', color);
    document.documentElement.style.setProperty('--light-color', light_color);
    document.documentElement.style.setProperty('--hover-color', hover_color);
    document.documentElement.style.setProperty('--menu-list-color', menu_list_color);
}

function goBack() {
    window.history.back()
}


$(".uploaded_file").change(function () {
    $(".uButton").attr("disabled", false);
    $('.uLabel').text("");
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        var file = $('#id_file')[0].files[0];

        if (file && file.size > 5242880) {
            $(".uButton").attr("disabled", true);
            $('.uLabel').text("File " + file.name + " of type " + file.type + " must be less than 5Mbs");
            return false;
        }
    }
});

$("#hImage").change(function (e) {
    var file, img, fileSize;
    fileSize = (this.files[0].size) / 1048576;
    if ((file = this.files[0])) {
        img = new Image();
        var objectUrl = _URL.createObjectURL(file);
        img.onload = function () {
            if (this.height > 1000 && fileSize <= 2) {
                $("#hButton").attr("disabled", false);
                $('#hLabel').text("");
            } else {
                if (fileSize > 2) {
                    $('#hLabel').text("Image size should be less than 2 MB");
                } else {
                    $('#hLabel').text("Image short side edge at least 2000px");
                }
                $('#hButton').attr('disabled', true);
            }
            _URL.revokeObjectURL(objectUrl);
        };
        img.onerror = function () {
            $('#hButton').attr('disabled', true);
            $('#hLabel').text("File should be an image,");
        };
        img.src = objectUrl;
    }
});