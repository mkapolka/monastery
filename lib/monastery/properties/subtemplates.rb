require_relative 'property.rb'

module Properties
    class SubtemplateProperty < Property
        def subtemplate=(subtemplate_class)
            if @subtemplate != nil
                @subtemplate.unapply(self.owner)
            end
            @subtemplate = subtemplate_class
            if @subtemplate != nil
                @subtemplate.apply(self.owner)
            end
        end

        def subtemplate
            return @subtemplate
        end

        def make(me)
            super
            if self.subtemplate != nil
                subtemplate.apply(me)
            end
        end

        def unmake(me)
            super
            if self.subtemplate != nil
                subtemplate.unapply(me)
            end
        end
    end

    class Form < SubtemplateProperty
    end

    class Material < SubtemplateProperty
    end
end
