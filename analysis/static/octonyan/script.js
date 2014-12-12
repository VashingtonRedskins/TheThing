

$(function () {
    function sort(){
        var i, j, k, a;
        a = arguments[0];
        for(i = 0; i < a.length; i++){
            for(j = 0; j < a.length; j++){
                if(a[i][0] < a[j][0]){
                    k = a[i];
                    a[i]=a[j];
                    a[j]=k;
                }
            }
        }
        return a;
    }
    function getSt(array, t){
        var d = [];
        for(var i=0; i< array.length; i++){
            d.push({
                name:array[i].name,
                //name: typeof t == 'string'? t[i]: array[i].name,
                data:(function(){
                    var a = [];
                    for(var j=0; j< array[i].commit.length; j++){
                        var d = new Date(array[i].commit[j].date);
                        a.push([
                            array[i].commit[j].date,
                            array[i].commit[j][t]
                        ])
                    }
                    return sort(a);
                })()
            });
        }
        return d;
    }
    function getTotal(array, st){
        var i, j, l, d=[],k={};
        for(i in st){
            k[st[i]] = {name:st[i], data:[]};
        }
        for(i=0;i<array.length;i++){
            for(j=0;j<array[i].commit.length;j++){
                for(l in st){
                    k[st[l]].data.push([
                        array[i].commit[j].date,
                        array[i].commit[j][st[l]]
                    ])
                }
            }
        }
        for(i in k){
            k[i].data = sort(k[i].data);
            d.push(k[i]);
        }
        return d;
    }
    function normData(rep, st){
        var i, j, k, c;
        for (i=0;i<rep.length;i++){
            for(j=0;j<rep[i].commit.length;j++){
                c = rep[i].commit[j];
                for (k in st){
                    c[st[k]]/=100;
                }
                k = new Date(c.date);
                c.date = Date.UTC(
                    k.getYear(), k.getMonth(), k.getDate()
                )

            }
        }
    }
    var st = ['pep8', 'pep257', 'docstring']; //
    normData(rep, st);
    var i;
    $('#total').highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'total'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                month: '%b',
                year: '%b'
            }
            ,
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Соответсвие %'
            },
            min: 0,
            max:100
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e %b}: {point.y:.2f} %'
        },

        series: getTotal(rep, st)
    });
    for(i in st){
        $('#'+st[i]).highcharts({
            chart: {
                type: 'spline'
            },
            title: {
                text: st[i]
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    month: '%b',
                    year: '%b'
                }
                ,
                title: {
                    text: 'Date'
                }
            },
            yAxis: {
                title: {
                    text: 'Соответсвие %'
                },
                min: 0,
                max:100
            },
            tooltip: {
                headerFormat: '<b>{series.name}</b><br>',
                pointFormat: '{point.x:%e %b}: {point.y:.2f} %'
            },

            series: getSt(rep, st[i])
        });
    }

});