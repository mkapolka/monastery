module Properties
   class Sentient < Property
      types :psychological
      description "is sentient"

      upon :tick do |me|
         puts "think"
         me.do :think, me if me.alive? 
         me.say "#{me.name} thinks.", :say;
      end
   end
end

module Forms
   form :brain do |me|
     is :sentient 
     lends_properties :psychological
   end
end
