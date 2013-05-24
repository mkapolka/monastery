module Properties
   class Player_Soul < Property
      @@souls = [];
      @@current_player_soul = nil;

      description "has a soul"
      revealed_by :magic
      type :soul

      def self.souls
         return @@souls
      end

      upon :make do |me|
         @@souls.push(self);
         @@current_player_soul = self;
      end

      upon :unmake do |me|
         @@souls.delete(self);
         @@current_player_soul = nil;
      end

      def self.current_player_soul
         return @@current_player_soul
      end
   end
end

def current_player
   return Properties::Player_Soul.current_player_soul.noun;
end

def look
   puts "You see here...\n"
   current_player.detect(:look).each do |what|
      puts "\t" + what.name
   end
end
