#include "cfg.h"

#if USE_AccelStepper

#include <Arduino.h>
#include <AccelStepper.h>
#include "AccelStepperClass.h"
#include <stdlib.h>

const char* nanpy::AccelStepperClass::get_firmware_id(){
    return "AccelStepper";
}

void nanpy::AccelStepperClass::elaborate( MethodDescriptor* m ) {
    ObjectsManager<AccelStepper>::elaborate(m);

    if (strcmp(m->getName(),"new") == 0) {
		AccelStepper as(m->getInt(0), m->getInt(1), m->getInt(2),m->getInt(3), m->getInt(4), m->getInt(5));
		v.insert(as);
        m->returns(v.getLastIndex());
    }
	
	// if (strcmp(m->getName(),"new") == 0) {
		// AccelStepper* as=new AccelStepper (m->getInt(0), m->getInt(1), m->getInt(2),m->getInt(3), m->getInt(4), m->getInt(5));
		// v.insert(as);
        // m->returns(v.getLastIndex());
    // }


    if (strcmp(m->getName(), "runSpeed") == 0) {
        //m->returns(v[m->getObjectId()]->runSpeed());
        m->returns(v[m->getObjectId()]->runSpeed());
    }
	
  
	if (strcmp(m->getName(), "setSpeed") == 0) {
      v[m->getObjectId()]->setSpeed(m->getInt(0));
      m->returns(0);
    }
	
	
	if (strcmp(m->getName(), "setMaxSpeed") == 0) {
        //m->returns(v[m->getObjectId()]->setSpeed(m->getInt(0)));
      v[m->getObjectId()]->setMaxSpeed(m->getInt(0));
	  m->returns(0);
    }

    if (strcmp(m->getName(), "stop") == 0) {
      v[m->getObjectId()]->stop();
    }




};

#endif
