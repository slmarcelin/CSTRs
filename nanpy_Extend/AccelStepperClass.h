#ifndef ACCELSTEPPER_CLASS
#define ACCELSTEPPER_CLASS

#include "BaseClass.h"
#include "MethodDescriptor.h"

class AccelStepper;

namespace nanpy {
    class AccelStepperClass: public ObjectsManager<AccelStepper> {
        public:
            void elaborate( nanpy::MethodDescriptor* m );
            const char* get_firmware_id();
    };
}

#endif
