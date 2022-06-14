import json
from flask import Flask, render_template
from flask import request

import shotgun_api3


app=Flask(__name__)

sg= shotgun_api3.Shotgun(
        "https://icentric-dev.shotgrid.autodesk.com",
        script_name="delSequence",
        api_key="bay_kprwfejlqkypbwMchbz3x",
        )

@app.route('/delSequence',methods=['POST'])
def delSequence():
    try:
        dataDictForm= dict(request.form.to_dict())
        selectedIds=dataDictForm['selected_ids'].split(',')                                                     

        req = {'sequence':[],'shots':[]}                                                               
        for SeqID in selectedIds:
            filters =[                                                                              
                ['project', 'is', {'type': 'Project', 'id': int(dataDictForm['project_id'])}],
                ['id','is',int(SeqID)]
            ]
            fields= ['code','shots']

            sg_Seq=sg.find_one('Sequence',filters,fields)                                                
            
            if sg_Seq is not None:
                sg_Shots=sg_Seq['shots']                                                                     
                for sg_Shot in sg_Shots:                      
                    sg_Shot['Episode']=sg_Seq['code']                                                      
                    sg_shotExtend=sg.find_one('Shot',[['id', 'is', int(sg_Shot['id'])]],['image'])
                    image=sg_shotExtend['image']                                                            
                    if image == None:                                                                       
                        sg_Shot['image']="None"
                    else:                                                                                  
                        sg_Shot['image']=image
                    sg_Shot.pop('type')                                                                    
                    req['shots'].append(sg_Shot)                                                           


                sg_Seq.pop('shots')
                req['sequence'].append(sg_Seq)
        
        
    
        return render_template("delSequence.html", data=req,size=len(req['shots']))
    except Exception as e:
        return render_template("error.html", data=req)       
    except shotgun_api3.ShotgunError or Exception as e:
        return render_template("error.html", data=req)                                              
    
@app.route('/delImplement',methods=['POST'])
def delImplement():
    dataDictForm=dict(request.form.to_dict())
    idLen = int(dataDictForm['IdLen'])
    seqIdLen = int(dataDictForm['seqIDLen'])

    for i in range(0,idLen):
        nextKey = 'Ids['+str(i)+']'
        sg.delete('Shot',int(dataDictForm[nextKey]))

    for i in range(0,seqIdLen):
        nextKey = 'seqID['+str(i)+']'
        sg.delete('Sequence',int(dataDictForm[nextKey]))

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


if __name__=='__main__':
    app.run(host="0.0.0.0")
